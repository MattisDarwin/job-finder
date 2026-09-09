#!/usr/bin/env python3
"""Interroge les API publiques des sites carrière et verse les offres pertinentes.

Les six grandes plateformes de recrutement publient une API JSON SANS authentification :
les entreprises veulent que leurs offres soient lues, c'est ainsi qu'elles se diffusent.
On ne scrape donc rien — on utilise l'usage prévu.

Usage : python3 sites-carriere.py [--tout]
  sans argument : n'ajoute que les offres qui collent au profil et au lieu
  --tout        : n'applique aucun filtre (pour voir ce qu'il y a)
"""
import concurrent.futures as cf
import datetime
import hashlib
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

RACINE = pathlib.Path(__file__).resolve().parent
DATA, REGISTRE = RACINE / "data.js", RACINE / "sites-carriere.json"
PREFIXE = "const DATA = "

# --- le profil de recherche ---------------------------------------------------
# Ce qui décide qu'une offre entre ou non ne vit PAS dans ce fichier : il est dans
# `profil.json`, à côté. C'est le seul endroit à modifier pour adapter l'outil à
# quelqu'un d'autre — voir `profil.exemple.json` pour un modèle commenté.
#
# Le tri est volontairement grossier : il enlève ce qui ne peut pas convenir, pas plus.
# On trie ensuite à la main — mieux vaut dix offres à écarter qu'une bonne manquée.
# Tout est cherché en limites de mots : « ai » doit matcher « AI Manager » mais pas
# « Certain ». Et tout existe en deux langues : sur un même site carrière on trouve
# « intelligence artificielle » et « artificial intelligence ».
PROFIL_DEFAUT = RACINE / "profil.json"
PROFIL_EXEMPLE = RACINE / "profil.exemple.json"


def charger_profil(chemin=None):
    """Le profil, ou l'exemple s'il n'y en a pas encore — pour que le premier lancement
    marche sans rien configurer."""
    p = pathlib.Path(chemin) if chemin else PROFIL_DEFAUT
    if not p.exists():
        if not PROFIL_EXEMPLE.exists():
            raise SystemExit(f"Aucun profil : ni {p.name}, ni {PROFIL_EXEMPLE.name}.")
        print(f"  (pas de {p.name} : on utilise {PROFIL_EXEMPLE.name})")
        p = PROFIL_EXEMPLE
    return json.loads(p.read_text())


PROFIL = charger_profil()


def _ou(motifs):
    """Une liste de motifs devient une alternance. Compilée sans le mode verbeux :
    dans un fichier JSON, un espace est un espace."""
    return re.compile("|".join(motifs), re.I) if motifs else re.compile(r"(?!)")


GARDE_RE = _ou(PROFIL["garde"])
ECARTE_RE = _ou(PROFIL["ecarte"])
LANGUE_AUTRE = _ou(PROFIL.get("langues_ecartees", []))
LIEUX = tuple(x.lower() for x in PROFIL.get("lieux", []))
PLAFOND = PROFIL.get("plafond_par_entreprise", 25)
VIE_PARTOUT = PROFIL.get("vie_partout", True)


# --- le type de contrat ------------------------------------------------------
# Il se lit dans l'intitulé, seule chose qu'on stocke. « VIE » est cherché en
# respectant la casse : sinon « qualité de vie au travail » deviendrait un VIE.
VIE_SIGLE = re.compile(r"\bV\.?I\.?E\b")
VIE_MOTS = re.compile(r"volontariat\s+international|international\s+volunteer", re.I)
CDD_RE = re.compile(r"\bCDD\b")
CDI_RE = re.compile(r"\bCDI\b")


def contrat(titre):
    """Rend « VIE », « CDD », « CDI » ou « » quand l'intitulé ne dit rien."""
    t = titre or ""
    if VIE_SIGLE.search(t) or VIE_MOTS.search(t):
        return "VIE"
    if CDD_RE.search(t):
        return "CDD"
    if CDI_RE.search(t):
        return "CDI"
    return ""


def pertinent(titre, lieu, tout=False):
    """Le tri se fait sur l'intitulé seul. Lire les descriptions a été essayé puis
    abandonné : le texte de présentation de l'entreprise portait les signaux, pas le
    poste, et le rendement était d'une bonne offre pour trois — voir decisions.md."""
    if tout:
        return True
    t, l = titre or "", (lieu or "").lower()
    # Un VIE est un poste à l'étranger par définition : le limiter à la France et à la
    # Suisse n'a pas de sens. C'est ainsi qu'on serait passé à côté du VIE Mantu à Porto,
    # celui qui a rendu le premier entretien. Le tri du pays se fait dans la page.
    if not (VIE_PARTOUT and contrat(t) == "VIE") and not any(x in l for x in LIEUX):
        return False
    if LANGUE_AUTRE.search(t) or ECARTE_RE.search(t):
        return False
    return bool(GARDE_RE.search(t))


# --- découpage du lieu -------------------------------------------------------
# Chaque plateforme écrit le lieu à sa façon ("Paris, France", "Paris, Paris, France",
# "Remote - EMEA"). On en tire trois champs stables : pays / région / ville.
PAYS = {"france": "France", "switzerland": "Suisse", "suisse": "Suisse", "schweiz": "Suisse",
        "germany": "Allemagne", "deutschland": "Allemagne", "allemagne": "Allemagne",
        "spain": "Espagne", "espagne": "Espagne", "italy": "Italie", "italie": "Italie",
        "united kingdom": "Royaume-Uni", "uk": "Royaume-Uni", "england": "Royaume-Uni",
        "netherlands": "Pays-Bas", "belgium": "Belgique", "belgique": "Belgique",
        "united states": "États-Unis", "usa": "États-Unis", "portugal": "Portugal",
        "poland": "Pologne", "ireland": "Irlande", "sweden": "Suède", "austria": "Autriche"}
REGIONS = {"paris": "Île-de-France", "boulogne": "Île-de-France", "issy": "Île-de-France",
           "levallois": "Île-de-France", "courbevoie": "Île-de-France", "nanterre": "Île-de-France",
           "saint-denis": "Île-de-France", "montrouge": "Île-de-France", "versailles": "Île-de-France",
           "lyon": "Auvergne-Rhône-Alpes", "grenoble": "Auvergne-Rhône-Alpes",
           "annecy": "Auvergne-Rhône-Alpes", "clermont": "Auvergne-Rhône-Alpes",
           "lille": "Hauts-de-France", "bordeaux": "Nouvelle-Aquitaine",
           "nantes": "Pays de la Loire", "rennes": "Bretagne", "toulouse": "Occitanie",
           "montpellier": "Occitanie", "marseille": "Provence-Alpes-Côte d'Azur",
           "nice": "Provence-Alpes-Côte d'Azur", "sophia": "Provence-Alpes-Côte d'Azur",
           "strasbourg": "Grand Est", "nancy": "Grand Est", "metz": "Grand Est",
           "geneva": "Genève", "genève": "Genève", "lausanne": "Vaud", "zurich": "Zurich",
           "zürich": "Zurich", "basel": "Bâle", "bâle": "Bâle", "bern": "Berne"}


# Deux graphies d'une même ville font deux filtres : « Zürich » et « Zurich » côte à côte.
CANON = {"zurich": "Zurich", "zürich": "Zurich", "geneva": "Genève", "genève": "Genève",
         "genf": "Genève", "basel": "Bâle", "bâle": "Bâle", "bale": "Bâle",
         "bern": "Berne", "berne": "Berne", "lausanne": "Lausanne", "london": "Londres",
         "munich": "Munich", "münchen": "Munich", "koln": "Cologne", "köln": "Cologne"}


REGIONS_VILLE = {}          # rempli juste après REGIONS


def _propre(ville):
    """Nettoie ce que les plateformes collent au nom de ville : drapeaux, « offices »,
    parenthèses de télétravail. Sans ça le filtre affiche « Lyon » et « Lyon 🇫🇷 » à part."""
    v = re.sub(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]", "", ville)
    v = re.sub(r"\s*\([^)]*\)", "", v)
    v = re.sub(r"\b(offices?|bureaux|hq|siège|area|region|métropole)\b", "", v, flags=re.I)
    # « 9th arrondissement of Paris », « Paris 9e » : c'est Paris
    v = re.sub(r"^.*\barrondissement\s+(of|de|du)\s+", "", v, flags=re.I)
    v = re.sub(r"\s+\d{1,2}(er|e|ème|th|nd|rd)?$", "", v, flags=re.I)
    if re.fullmatch(r"(all|toute la)\s+\w+", v, flags=re.I):   # « All France » = pas une ville
        return ""
    v = re.sub(r"\s{2,}", " ", v).strip(" -,")
    # RATP écrit l'adresse du bâtiment en guise de ville : on garde ce qui suit le « : »
    if ":" in v:
        v = v.split(":")[-1].strip()
    # une adresse reste une adresse — on y cherche une ville connue, sinon on renonce
    if len(v) > 28 or any(c.isdigit() for c in v):
        connue = next((REGIONS_VILLE[k] for k in REGIONS_VILLE if k in v.lower()), "")
        v = connue
    if v.isupper():                     # « PARIS » et « Paris » sont la même ville
        v = v.title()
    return CANON.get(v.lower(), v)


REGIONS_VILLE.update({k: k.capitalize() for k in REGIONS})


def decoupe_lieu(lieu):
    """Retourne (pays, région, ville) à partir d'un lieu écrit librement."""
    l = (lieu or "").strip()
    bas = l.lower()
    if not l or l == "?":
        return "?", "", ""
    mots = set(re.findall(r"[a-zà-ÿ]+", bas))
    trouve = next((v for k, v in PAYS.items()
                   if (k in mots if " " not in k else k in bas)), "")
    if "remote" in mots and not trouve:
        return "Remote", "", ""

    pays = trouve
    bouts = [b.strip() for b in l.replace(" - ", ",").split(",") if b.strip()]
    # la ville est le premier morceau, sauf s'il nomme déjà le pays
    ville = ""
    for b in bouts:
        if b.lower() in PAYS or b.lower() == "remote":
            continue
        ville = _propre(b)
        if ville and ville.lower() not in PAYS:   # « Germany (remote) » n'est pas une ville
            break
        ville = ""
    region = next((v for k, v in REGIONS.items() if k in (ville or "").lower()), "")
    if not pays and region:
        pays = "Suisse" if region in ("Genève", "Vaud", "Zurich", "Bâle", "Berne") else "France"
    return pays or "?", region, ville


# --- les cinq plateformes ----------------------------------------------------
# Une entreprise perdue pour la passe, c'est un mois d'offres qu'on ne verra jamais — et
# ça arrivait sur un simple hoquet. Workday se retentait déjà tout seul (`_wd`) ; on donne
# la même seconde chance à tout le monde. On ne retente QUE ce qui peut passer au second
# essai : une panne réseau, un 5xx, un 429. Pas un 403 : celui-là tient à la requête
# requêtes. Un 404 est une réponse — la retenter ne ferait que perdre du temps.
RETENTABLES = {408, 429, 500, 502, 503, 504}

# Un « Mozilla/5.0 » tout seul n'est pas un navigateur, et les pare-feux applicatifs le
# savent : careers.se.com rendait 403 à chaque fois sur cet en-tête, et 200 à chaque fois
# sur celui-ci. Ce n'était pas du débit — c'était la signature. On annonce donc un vrai
# navigateur, partout et de la même façon.
NAVIGATEUR = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")


def _reessaie(faire, essais=2, pause=0.8):
    for essai in range(essais):
        try:
            return faire()
        except urllib.error.HTTPError as e:
            if e.code not in RETENTABLES or essai + 1 == essais:
                raise
        except Exception:
            if essai + 1 == essais:
                raise
        time.sleep(pause)


def _get_brut(url):
    def une():
        req = urllib.request.Request(url, headers={"User-Agent": NAVIGATEUR})
        with urllib.request.urlopen(req, timeout=40) as r:
            return r.read()
    return _reessaie(une)


def _get(url):
    def une():
        req = urllib.request.Request(url, headers={"User-Agent": NAVIGATEUR})
        with urllib.request.urlopen(req, timeout=25) as r:
            return json.loads(r.read())
    return _reessaie(une)


def greenhouse(s):
    d = _get(f"https://boards-api.greenhouse.io/v1/boards/{s}/jobs?content=false")
    return [(j.get("title"), (j.get("location") or {}).get("name"), j.get("absolute_url"),
             (j.get("updated_at") or "")[:10]) for j in d.get("jobs", [])]

def lever(s):
    d = _get(f"https://api.lever.co/v0/postings/{s}?mode=json")
    return [(j.get("text"), (j.get("categories") or {}).get("location"), j.get("hostedUrl"),
             datetime.datetime.fromtimestamp((j.get("createdAt") or 0)/1000).strftime("%Y-%m-%d")
             if j.get("createdAt") else "") for j in d]

def smartrecruiters(s):
    out, offset = [], 0
    while True:
        d = _get(f"https://api.smartrecruiters.com/v1/companies/{s}/postings?limit=100&offset={offset}")
        lot = d.get("content", [])
        for j in lot:
            loc = j.get("location") or {}
            ville = ", ".join(x for x in [loc.get("city"), loc.get("country")] if x)
            out.append((j.get("name"), ville,
                        f"https://jobs.smartrecruiters.com/{s}/{j.get('id')}",
                        (j.get("releasedDate") or "")[:10]))
        offset += len(lot)
        if len(lot) < 100 or offset >= d.get("totalFound", 0):
            return out

def ashby(s):
    d = _get(f"https://api.ashbyhq.com/posting-api/job-board/{s}")
    return [(j.get("title"), j.get("location"), j.get("jobUrl"),
             (j.get("publishedAt") or "")[:10]) for j in d.get("jobs", [])]

def recruitee(s):
    d = _get(f"https://{s}.recruitee.com/api/offers/")
    return [(j.get("title"), j.get("location"), j.get("careers_url"),
             (j.get("published_at") or "")[:10]) for j in d.get("offers", [])]

# --- Workday ------------------------------------------------------------------
# L'ATS des grands groupes. Trois différences avec les cinq autres : l'adresse ne se
# devine pas (tenant/cluster/site, voir decouvrir-workday.py), la requête est un POST,
# et la page plafonne à 20 offres.
#
# Un groupe publie des centaines d'offres dans le monde entier ; sans filtre on ramène
# Bogota et Chennai. Workday sait filtrer par pays, mais les identifiants de pays sont
# propres à chaque tenant — on ne peut pas les écrire en dur. Le premier appel, à vide,
# renvoie la liste des facettes : on y lit les identifiants de la France et de la Suisse,
# puis on repose la question avec le filtre. Deux temps, et plus rien d'inutile.
WD_PAYS = ("France", "Switzerland", "Suisse", "Schweiz")
WD_PAGES = 15          # 15 × 20 = 300 offres par entreprise, au-delà c'est du bruit


def _wd(api, corps, essais=2):
    for essai in range(essais):
        req = urllib.request.Request(api, data=json.dumps(corps).encode(), method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json",
                                              "User-Agent": NAVIGATEUR})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                return json.loads(r.read())
        except Exception:
            if essai + 1 == essais:
                raise
            time.sleep(0.6)


# Workday ne donne pas toujours « startDate » : certains tenants n'exposent que le
# relatif, « Posted Yesterday », « Posted 12 Days Ago ». C'est convertible sans requête
# de plus. Au-delà de 30 jours il n'annonce que « 30+ » : on le dit tel quel plutôt que
# d'inventer une date fausse.
WD_RELATIF = re.compile(r"posted\s+(today|yesterday|(\d+)\+?\s+days?\s+ago)", re.I)


def _wd_date(j):
    if j.get("startDate"):
        return j["startDate"][:10]
    m = WD_RELATIF.search(j.get("postedOn") or "")
    if not m:
        return ""
    mot = m.group(1).lower()
    if mot == "today":
        return datetime.date.today().isoformat()
    if mot == "yesterday":
        return (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    jours = int(m.group(2))
    if "+" in (j.get("postedOn") or ""):
        return "30+"                        # Workday plafonne, on ne devine pas
    return (datetime.date.today() - datetime.timedelta(days=jours)).isoformat()


def _wd_facettes(d):
    """Aplatit l'arbre des facettes en (paramètre, valeurs). Chaque tenant a le sien :
    « locationCountry » sous locationMainGroup chez Sanofi, « Location_Country » au
    premier niveau chez Michelin, et rien du tout chez Roche."""
    out = []
    def descendre(noeuds):
        for f in noeuds or []:
            if not isinstance(f, dict):
                continue
            vals = f.get("values") or []
            if f.get("facetParameter") and any(v.get("id") for v in vals if isinstance(v, dict)):
                out.append((f["facetParameter"], vals))
            descendre(vals)
    descendre(d.get("facets"))
    return out


def _wd_filtre_lieu(d):
    """Retourne (paramètre, identifiants) pour ne garder que la France et la Suisse.

    Deux niveaux de repli : le filtre par pays quand il existe, sinon le filtre par ville
    en réutilisant LIEUX. Sans facette de lieu du tout, on rend None et l'appelant
    paginera à l'aveugle."""
    facettes = _wd_facettes(d)
    for param, vals in facettes:
        if "country" in param.lower():
            ids = [v["id"] for v in vals if v.get("descriptor") in WD_PAYS and v.get("id")]
            if ids:
                return param, ids
    for param, vals in facettes:
        if "location" in param.lower():
            ids = [v["id"] for v in vals
                   if v.get("id") and any(x in (v.get("descriptor") or "").lower() for x in LIEUX)]
            if ids:
                return param, ids
    return None, []


def workday(s):
    """`s` a la forme « tenant/cluster/site », produite par decouvrir-workday.py."""
    tenant, cluster, site = s.split("/")
    base = f"https://{tenant}.{cluster}.myworkdayjobs.com"
    api = f"{base}/wday/cxs/{tenant}/{site}/jobs"

    vide = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
    param, ids = _wd_filtre_lieu(_wd(api, vide))
    # sans facette de lieu on pagine quand même : `pertinent()` triera sur le titre
    facettes = {param: ids} if ids else {}

    out, total = [], 0
    for page in range(WD_PAGES):
        d = _wd(api, {"appliedFacets": facettes, "limit": 20,
                      "offset": page * 20, "searchText": ""})
        lot = d.get("jobPostings") or []
        total = total or d.get("total") or 0    # le compte n'arrive que sur la 1re page
        for j in lot:
            chemin = j.get("externalPath")
            if chemin:
                out.append((j.get("title"), j.get("locationsText"),
                            f"{base}/en-US/{site}{chemin}", _wd_date(j)))
        if len(lot) < 20 or (page + 1) * 20 >= total:
            break
    return out


# --- Talentsoft / Cegid -------------------------------------------------------
# L'ATS des grands groupes français : EDF, Crédit Agricole. Sa page de résultats est
# rendue par le serveur en ASP.NET, illisible sans navigateur — mais le site publie des
# **flux RSS**, la voie prévue et propre. Le flux rend 20 offres par défaut ; `top=`
# monte jusqu'à 1000, ce qui suffit. Le lieu n'est pas dans le flux : il est dans le
# titre ou dans la description, on le cherche là.
TS_MAX = 1000
BALISES_RSS = re.compile(r"<[^>]+>")
TS_LIEU = re.compile(r"\b(" + "|".join(("paris", "lyon", "lille", "bordeaux", "nantes",
    "marseille", "toulouse", "grenoble", "rennes", "strasbourg", "montpellier", "nice",
    "france", "suisse", "gen[èe]ve", "lausanne", "z[üu]rich", "b[âa]le")) + r")\b", re.I)


def talentsoft(s):
    """`s` est le nom d'hôte, par ex. « edf-recrute.talent-soft.com »."""
    d = _get_brut(f"https://{s}/handlers/offerRss.ashx?LCID=1036&top={TS_MAX}")
    out = []
    for it in ET.fromstring(d).findall(".//item"):
        titre = (it.findtext("title") or "").strip()
        # le flux préfixe l'intitulé de la référence interne : « 2026-180919 - HR Officer »
        titre = re.sub(r"^[A-Z0-9-]{6,24}\s*-\s*", "", titre)
        lien = (it.findtext("link") or "").strip()
        texte = BALISES_RSS.sub(" ", it.findtext("description") or "")
        m = TS_LIEU.search(titre) or TS_LIEU.search(texte)
        date = (it.findtext("pubDate") or "")
        if lien:
            out.append((titre, m.group(0) if m else "France", lien, _date_rss(date)))
    return out


def _date_rss(brut):
    for f in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S GMT"):
        try:
            return datetime.datetime.strptime(brut.strip(), f).strftime("%Y-%m-%d")
        except Exception:
            pass
    return ""


# --- Phenom People -----------------------------------------------------------
# Phenom n'est pas un ATS mais la vitrine posée devant : ABB affiche du Phenom et
# postule sur Workday. Sa recherche passe par un POST sur /widgets du site carrière
# lui-même — donc l'identifiant, c'est le nom d'hôte, rien à deviner.
# Le paramètre qui compte est "jobs": true ; sans lui la réponse annonce le nombre
# total d'offres et n'en renvoie aucune.
PHENOM_PAGE = 100


def phenom(hote):
    """`hote` est le nom de domaine du site carrière, par ex. « careers.abb »."""
    out = []
    for depart in range(0, 600, PHENOM_PAGE):
        corps = json.dumps({"ddoKey": "refineSearch", "from": depart, "size": PHENOM_PAGE,
                            "searchText": "", "locale": "en_global", "deviceType": "desktop",
                            "country": "global", "pageName": "search-results",
                            "jobs": True, "eagerLoadRefineSearch": True}).encode()
        req = urllib.request.Request(f"https://{hote}/widgets", data=corps, method="POST",
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json",
                                              "User-Agent": NAVIGATEUR,
                                              "Referer": f"https://{hote}/"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                d = (json.loads(r.read()).get("refineSearch") or {})
        except Exception:
            break
        lot = (d.get("data") or {}).get("jobs") or []
        for j in lot:
            lieu = (j.get("cityStateCountry") or j.get("location") or j.get("cityState")
                    or j.get("city") or j.get("country") or "")
            # Certains sites livrent l'URL, d'autres pas du tout (Kühne+Nagel) : on la
            # reconstruit alors depuis jobSeqNo, la forme d'adresse standard de Phenom.
            url = j.get("applyUrl") or j.get("jobSeoUrl")
            if not url and j.get("jobSeqNo"):
                url = f"https://{hote}/global/en/job/{j['jobSeqNo']}"
            if not url:
                continue
            out.append((j.get("title"), lieu, url, (j.get("postedDate") or "")[:10]))
        if len(lot) < PHENOM_PAGE or depart + PHENOM_PAGE >= (d.get("totalHits") or 0):
            break
    return out


# --- Teamtailor ---------------------------------------------------------------
# L'ATS des scale-ups européennes. Il publie un JSON Feed sur /jobs.json — la voie
# prévue, aucun jeton. Le lieu n'est pas au premier niveau : il est dans le bloc
# schema.org `_jobposting`, celui que Google lit pour afficher l'offre dans ses résultats.
# On y prend la ville et le pays, et on les recolle comme les autres plateformes les
# écrivent, pour que `decoupe_lieu()` s'y retrouve.
# schema.org veut le pays en code ISO : « Barcelona, ES ». Le reste du script lit des pays
# écrits en toutes lettres, et `decoupe_lieu()` rendrait « ? ». On traduit ici, là où on
# SAIT que c'est un code — élargir la table commune ferait de « es » un mot de pays partout.
TT_PAYS = {"FR": "France", "CH": "Switzerland", "ES": "Spain", "GB": "United Kingdom",
           "UK": "United Kingdom", "DE": "Germany", "IT": "Italy", "BE": "Belgium",
           "NL": "Netherlands", "PT": "Portugal", "IE": "Ireland", "US": "United States",
           "PL": "Poland", "SE": "Sweden", "AT": "Austria"}


def teamtailor(hote):
    """`hote` est le nom d'hôte du site carrière, par ex. « careers.payfit.com »."""
    d = _get(f"https://{hote}/jobs.json")
    out = []
    for it in d.get("items", []):
        jp = it.get("_jobposting") or {}
        lieux = jp.get("jobLocation") or []
        if isinstance(lieux, dict):
            lieux = [lieux]
        bouts = []
        for place in lieux:
            adr = (place or {}).get("address") or {}
            pays = adr.get("addressCountry") or ""
            if isinstance(pays, dict):                  # parfois un objet Country
                pays = pays.get("name") or ""
            bouts.append(", ".join(x for x in [adr.get("addressLocality"),
                                               TT_PAYS.get(pays.upper(), pays)] if x))
        lieu = " / ".join(dict.fromkeys(b for b in bouts if b))
        if it.get("url"):
            out.append((it.get("title"), lieu, it["url"], (it.get("date_published") or "")[:10]))
    return out


# --- Radancy / TalentBrew -----------------------------------------------------
# La vitrine que les grands groupes posent devant leur ATS — Veolia et bien d'autres.
# Sa page de résultats se peuple par un appel qui rend du HTML : on ne le lit pas. Le site
# publie aussi un **flux RSS** qui rend TOUTES les offres en une requête, la voie prévue.
# Particularité : le lieu n'a pas de balise à lui, il est collé au titre entre parenthèses
# — « Chef de projet - (Paris, Île-de-France, France) ». On le détache.
RADANCY_LIEU = re.compile(r"^(.*?)\s*[-–]\s*\(([^()]*)\)\s*$", re.S)


def radancy(hote):
    """`hote` est le nom d'hôte du site carrière, par ex. « jobs.veolia.com »."""
    d = _get_brut(f"https://{hote}/rss")
    out = []
    for it in ET.fromstring(d).findall(".//item"):
        brut = (it.findtext("title") or "").strip()
        lien = (it.findtext("link") or "").strip()
        m = RADANCY_LIEU.match(brut)
        titre, lieu = (m.group(1).strip(), m.group(2).strip()) if m else (brut, "")
        if lien:
            out.append((titre, lieu, lien, _date_rss(it.findtext("pubDate") or "")))
    return out


# --- Jibe ---------------------------------------------------------------------
# Le moteur de recherche que posent AXA et Schneider Electric. Comme Phenom, ce n'est pas
# l'ATS mais la vitrine : AXA postule sur Taleo, ses offres brésiliennes sur iCIMS. Peu
# importe — c'est ici que toutes les offres sont interrogeables d'un coup.
# Une page rendue en Angular (`ng-app="jibeapply"`) sert /api/jobs en JSON, et elle sait
# filtrer par pays avec le nom en anglais. Sans ce filtre on ramène le monde entier.
JIBE_PAGE = 100
JIBE_PAYS = ("France", "Switzerland")
JIBE_PAGES = 6          # 6 × 100 par pays ; au-delà c'est du bruit, comme le plafond Workday

# On pagine avec `page`, pas avec `offset` : AXA ignore `offset` en silence et resert
# éternellement la première page — 800 offres lues pour 200 distinctes, sans une erreur.
# `page` avance chez les deux, sans chevauchement.
#
# Et la date se lit à deux endroits : AXA écrit `posted_date` en ISO, Schneider l'écrit en
# toutes lettres — « August 4, 2026 » — que `[:10]` tronquait en « August 4, ». On tente
# l'ISO, puis l'anglais, puis on se rabat sur `create_date`, toujours en ISO.
def _jibe_date(o):
    brut = (o.get("posted_date") or "").strip()
    if re.match(r"\d{4}-\d{2}-\d{2}", brut):
        return brut[:10]
    try:
        return datetime.datetime.strptime(brut, "%B %d, %Y").strftime("%Y-%m-%d")
    except ValueError:
        return (o.get("create_date") or "")[:10]


def jibe(hote):
    """`hote` est le nom d'hôte du site carrière, par ex. « jobs.axa.com »."""
    out = []
    for pays in JIBE_PAYS:
        vus = 0
        for page in range(1, JIBE_PAGES + 1):
            d = _get(f"https://{hote}/api/jobs?country={urllib.parse.quote(pays)}"
                     f"&limit={JIBE_PAGE}&page={page}")
            lot = d.get("jobs") or []
            for j in lot:
                o = j.get("data") or {}
                # PAS `apply_url` : il mène au formulaire de l'ATS de derrière — une page
                # iCIMS vide de toute description, qui répond 200 sans rien montrer. La
                # fiche lisible est sur le site Jibe lui-même, à /jobs/<slug>.
                if o.get("slug"):
                    out.append((o.get("title"), o.get("full_location") or o.get("city") or pays,
                                f"https://{hote}/jobs/{o['slug']}", _jibe_date(o)))
            vus += len(lot)
            if len(lot) < JIBE_PAGE or vus >= (d.get("totalCount") or 0):
                break
    return out


PLATEFORMES = {"greenhouse": greenhouse, "lever": lever, "smartrecruiters": smartrecruiters,
               "ashby": ashby, "recruitee": recruitee, "workday": workday,
               "phenom": phenom, "talentsoft": talentsoft, "teamtailor": teamtailor,
               "radancy": radancy, "jibe": jibe}


def lire():
    txt = DATA.read_text()
    i = txt.index(PREFIXE) + len(PREFIXE)
    j = txt.rindex("}") + 1
    return txt[:i], json.loads(txt[i:j]), txt[j:]


def identifiant(url):
    """Un identifiant stable, dérivé de l'URL.

    `hash()` de Python est **randomisé à chaque lancement** (PYTHONHASHSEED) : la même
    offre recevait un identifiant différent d'une passe à l'autre. Rien ne cassait tant
    que la déduplication se fait sur l'URL, mais un identifiant qui change n'est pas un
    identifiant. blake2s donne le même résultat partout, toujours.
    """
    return "sc-" + hashlib.blake2s(url.encode(), digest_size=6).hexdigest()


def _cle(nom):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", nom.lower())
                  .encode("ascii", "ignore").decode().replace("(ch)", ""))


def adresse_carriere(plat, ident):
    """L'adresse humaine du site carrière, pour que le bouton de la fiche marche."""
    if plat == "workday":
        tenant, cluster, site = ident.split("/")
        return f"https://{tenant}.{cluster}.myworkdayjobs.com/{site}"
    if plat in ("phenom", "talentsoft", "teamtailor", "radancy", "jibe"):
        return f"https://{ident}/"
    return {"greenhouse": f"https://job-boards.greenhouse.io/{ident}",
            "lever": f"https://jobs.lever.co/{ident}",
            "smartrecruiters": f"https://jobs.smartrecruiters.com/{ident}",
            "ashby": f"https://jobs.ashbyhq.com/{ident}",
            "recruitee": f"https://{ident}.recruitee.com/"}.get(plat, "")


def main():
    tout = "--tout" in sys.argv
    registre = json.loads(REGISTRE.read_text())
    reg = registre["entreprises"]           # les « ecartes » ne sont jamais interrogés
    entete, obj, queue = lire()
    connus = {o.get("url") for o in obj["offres"]}
    # Une offre déjà enregistrée n'est pas figée : si sa date de publication manquait et
    # que la plateforme la donne maintenant, la passe répare la fiche au lieu de l'ignorer.
    par_url = {o.get("url"): o for o in obj["offres"]}
    reparees = 0
    aujourdhui = datetime.date.today().isoformat()

    def une(item):
        nom, fiche = item
        plat = fiche["plateforme"]
        try:
            return nom, plat, PLATEFORMES[plat](fiche["id"]), None
        except Exception as e:
            return nom, plat, [], f"{type(e).__name__}"

    total_brut = ajoutes = 0
    with cf.ThreadPoolExecutor(max_workers=10) as ex:
        for nom, plat, postes, err in ex.map(une, reg.items()):
            if err:
                print(f"  {nom:<24} échec ({err})")
                continue
            total_brut += len(postes)
            gardes = 0
            for titre, lieu, url, date in postes:
                ancienne = par_url.get(url)
                if ancienne and date and "non disponible" in (ancienne.get("note") or ""):
                    ancienne["note"] = ancienne["note"].replace(
                        "date de publication non disponible",
                        "publiée il y a plus de 30 jours" if date == "30+"
                        else f"publiée le {date}")
                    reparees += 1

            retenues = [p for p in postes
                        if p[2] and p[2] not in connus and pertinent(p[0], p[1], tout)]
            retenues.sort(key=lambda p: p[3] or "", reverse=True)   # les plus récentes d'abord
            ecartees = max(0, len(retenues) - PLAFOND)
            for titre, lieu, url, date in retenues[:PLAFOND]:
                connus.add(url)
                pays, region, ville = decoupe_lieu(lieu)
                obj["offres"].append({
                    "id": identifiant(url),
                    "entreprise": nom, "poste": titre or "?", "lieu": lieu or "?",
                    "pays": pays, "region": region, "ville": ville, "ajoute": aujourdhui,
                    "teletravail": "oui" if "remote" in (lieu or "").lower() else "à vérifier",
                    "piste": "1 — planque", "statut": "a-voir", "priorite": 15, "url": url,
                    "contrat": contrat(titre),
                    "note": f"Site carrière ({plat}) · trouvée le {aujourdhui} · "
                            + ("publiée il y a plus de 30 jours" if date == "30+"
                               else f"publiée le {date}" if date
                               else "date de publication non disponible"),
                })
                gardes += 1
                ajoutes += 1
            trop = f" (+{ecartees} au-delà du plafond)" if ecartees else ""
            print(f"  {nom:<24} {len(postes):>4} offres → {gardes} gardées{trop}")

    # Une seule liste d'entreprises : toute entreprise interrogée doit avoir sa fiche,
    # sinon ses offres semblent venir de nulle part. On complète ce qui manque et on ne
    # touche jamais aux notes écrites à la main : c'est du travail humain.
    par_cle = {_cle(e["nom"]): e for e in obj["entreprises"]}
    for nom, fiche in sorted(reg.items(), key=lambda kv: kv[0].lower()):
        connue = par_cle.get(_cle(nom))
        if connue is None:
            connue = {"nom": nom, "url": adresse_carriere(fiche["plateforme"], fiche["id"]),
                      "note": ""}
            obj["entreprises"].append(connue)
        # les tags sont tenus dans le registre : la fiche les recopie, elle ne les invente pas
        connue["tags"] = fiche.get("tags", [])
    obj["branchees"] = sorted(reg)
    obj["ecartees"] = sorted(registre.get("ecartes", {}))
    # Ni branchées ni à brancher : la page doit pouvoir le dire, sinon son compteur de
    # « non branchées » annonce du travail qui n'existe pas.
    obj["agregateurs"] = registre.get("agregateurs", {})
    obj["sans_api"] = registre.get("sans_api", {})
    DATA.write_text(entete + json.dumps(obj, ensure_ascii=False, indent=2) + queue)
    print(f"\n{total_brut} offres lues · {ajoutes} ajoutées · {reparees} dates complétées"
          f" · {len(obj['offres'])} au total")


if __name__ == "__main__":
    main()
