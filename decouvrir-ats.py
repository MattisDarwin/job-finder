#!/usr/bin/env python3
"""Lit une page carrière et dit quel ATS se cache derrière.

`decouvrir.py` devine des identifiants et demande à cinq API si elles connaissent ce nom :
il ne trouve que ce qui s'appelle comme l'entreprise, et il confond les homonymes — une
startup de Palo Alto répond au nom « vinci ». `decouvrir-workday.py`, lui, ne sait chercher
qu'une seule plateforme.

Celui-ci fait l'inverse, et c'est la méthode qui a marché à la main pour ABB et EDF : on
part de l'adresse **notée dans la fiche de l'entreprise**, on suit les redirections, et on
lit la page. Un ATS laisse toujours sa trace — un nom de domaine, un script, un mot-clé.
Le résultat n'est donc jamais un homonyme : c'est ce que sert vraiment cette entreprise-là.

Ça ne rend pas un identifiant prêt à coller : ça dit quelle porte frapper, ce qui est le
travail long. La ligne du registre s'écrit ensuite, à la main, et se vérifie sur trois
offres réelles.

Usage : python3 decouvrir-ats.py [nom ...]
  sans argument : toutes les entreprises de data.js qui ne sont ni branchées, ni écartées,
  ni des agrégateurs.
"""
import concurrent.futures as cf
import json
import pathlib
import re
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

RACINE = pathlib.Path(__file__).resolve().parent
DATA = RACINE / "data.js"
ENTETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
           "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
           "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8"}

# Les empreintes, de la plus spécifique à la plus vague. L'ordre compte : « successfactors »
# apparaît dans des pages Taleo, mais pas l'inverse.
# (nom lisible, motif, ce qu'on sait en faire)
EMPREINTES = [
    ("workday",        r"myworkdayjobs\.com|workdaycdn\.com",      "branchable — decouvrir-workday.py"),
    ("greenhouse",     r"greenhouse\.io|boards\.greenhouse",       "branchable — identifiant dans l'URL"),
    ("lever",          r"jobs\.lever\.co|api\.lever\.co",          "branchable — identifiant dans l'URL"),
    ("smartrecruiters", r"smartrecruiters\.com",                   "branchable — identifiant dans l'URL"),
    ("ashby",          r"ashbyhq\.com",                            "branchable — identifiant dans l'URL"),
    ("recruitee",      r"recruitee\.com",                          "branchable — identifiant dans l'URL"),
    ("talentsoft",     r"talent-soft\.com|talentsoft\.com",        "branchable — flux RSS offerRss.ashx"),
    ("phenom",         r"phenompeople|phenom\.com|/phapp/|ph-widget", "branchable — POST /widgets"),
    ("teamtailor",     r"teamtailor\.com",                         "API publique /jobs.json — à écrire"),
    ("jibe",           r"jibeapply|ng-app=[\"']jibeapply",          "branchable — GET /api/jobs?country=France"),
    ("radancy",        r"radancy\.(eu|com)|talentbrew\.com|tbcdn\.", "branchable — flux RSS sur /rss"),
    ("successfactors", r"successfactors\.(com|eu)|jobs\.sap\.com|career\d*\.sap",
                                                                   "SAP — API OData, souvent fermée"),
    ("taleo",          r"taleo\.net|careersection",                "Oracle — jeton CSRF nécessaire"),
    ("avature",        r"avature\.net",                            "pas d'API publique connue"),
    ("icims",          r"icims\.com",                              "pas d'API publique connue"),
    ("brassring",      r"brassring\.com|kenexa",                   "pas d'API publique connue"),
    ("cornerstone",    r"csod\.com|cornerstoneondemand",           "pas d'API publique connue"),
    ("softgarden",     r"softgarden\.io",                          "API publique — à écrire"),
    ("welcometothejungle", r"welcometothejungle\.com",             "agrégateur — pas un ATS"),
    ("flatchr",        r"flatchr\.io",                             "API publique — à écrire"),
    ("jobvite",        r"jobvite\.com",                            "pas d'API publique connue"),
    ("eightfold",      r"eightfold\.ai",                           "API /api/apply/v2/jobs — à écrire"),
    ("beetween",       r"beetween\.com",                           "pas d'API publique connue"),
    ("digitalrecruiters", r"digitalrecruiters\.com",               "API publique — à écrire"),
]


def _cle(nom):
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", nom.lower())
                  .encode("ascii", "ignore").decode().replace("(ch)", ""))


def _lire(url, taille_max=600_000):
    """Rend (url finale après redirections, html). Une erreur HTTP a quand même un corps :
    une page 403 de Cloudflare ne dit rien, mais une 404 d'ATS dit souvent lequel."""
    req = urllib.request.Request(url, headers=ENTETES)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.geturl(), r.read(taille_max).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        try:
            return e.geturl(), e.read(taille_max).decode("utf-8", "replace")
        except Exception:
            return e.geturl(), ""


# Le lien vers l'ATS est rarement sur la page d'accueil carrière : il est derrière un
# bouton « voir nos offres ». On suit une fois les liens qui en ont l'air.
VERS_LES_OFFRES = re.compile(
    r"""<a[^>]+href\s*=\s*["']([^"']+)["'][^>]*>(?:(?!</a>).){0,120}"""
    r"""(nos\s+offres|toutes\s+les\s+offres|voir\s+les\s+offres|rechercher|search\s+jobs"""
    r"""|view\s+(all\s+)?jobs|open\s+positions|postuler|job\s+search|nos\s+m[ée]tiers)""",
    re.I | re.S)


NOTRE_MAISON = re.compile(r"google|gstatic|facebook|twitter|linkedin|youtube|doubleclick"
                          r"|cloudflare|jquery|bootstrap|fontawesome|typekit|hotjar|matomo"
                          r"|piwik|onetrust|cookiebot|adobedtm|demdex|omtrdc|newrelic|sentry"
                          r"|viadeo|instagram|tiktok|vimeo|addthis|trustpilot|didomi|axeptio", re.I)
TIERS = re.compile(r"""(?:src|href)\s*=\s*["']https?://([a-z0-9][a-z0-9.-]+\.[a-z]{2,})""", re.I)


def domaines_tiers(html, propre):
    """Les hôtes que la page appelle et qui ne sont ni elle-même ni du mobilier de web.
    C'est la liste dans laquelle se trouve l'ATS quand on ne le reconnaît pas encore."""
    racine = ".".join(propre.split(".")[-2:])
    vus = {}
    for h in TIERS.findall(html):
        h = h.lower()
        if racine in h or NOTRE_MAISON.search(h):
            continue
        vus[h] = vus.get(h, 0) + 1
    return sorted(vus, key=lambda h: -vus[h])[:6]


def _empreinte(texte):
    for nom, motif, quoi in EMPREINTES:
        if re.search(motif, texte, re.I):
            return nom, quoi
    return None, None


# La fiche pointe souvent la page corporate « nos carrières », pleine de photos
# et vide d'ATS : le moteur de recherche vit sur un sous-domaine à lui. On les essaie.
PREFIXES = ("jobs", "careers", "carrieres", "emploi", "emplois", "recrutement", "recrute")


def _voisins(finale):
    hote = urllib.parse.urlsplit(finale).netloc
    bouts = hote.split(".")
    racine = ".".join(bouts[-3:]) if hote.endswith((".gouv.fr", ".co.uk")) else ".".join(bouts[-2:])
    return [f"https://{p}.{racine}/" for p in PREFIXES if not hote.startswith(p + ".")]


def sonde(nom, url):
    """Rend (nom, ats, quoi, où) — ou (nom, None, raison, url) quand rien ne ressort."""
    try:
        finale, html = _lire(url)
    except Exception as e:
        return nom, None, f"injoignable ({type(e).__name__})", url
    ats, quoi = _empreinte(finale + " " + html)
    if ats:
        return nom, ats, quoi, finale

    # le moteur de recherche est peut-être sur un sous-domaine dédié
    for v in _voisins(finale):
        try:
            f3, h3 = _lire(v)
        except Exception:
            continue
        ats, quoi = _empreinte(f3 + " " + h3)
        if ats:
            return nom, ats, quoi, f3

    # rien en première page : on suit un lien « voir les offres », une seule fois
    for m in list(VERS_LES_OFFRES.finditer(html))[:4]:
        suite = urllib.parse.urljoin(finale, m.group(1))
        if suite.rstrip("/") == finale.rstrip("/"):
            continue
        try:
            f2, h2 = _lire(suite)
        except Exception:
            continue
        ats, quoi = _empreinte(f2 + " " + h2)
        if ats:
            return nom, ats, quoi, f2
    # dernière chance : frapper aux points d'entrée qu'on sait exploiter
    for h in hotes_plausibles(nom, finale):
        trouve = frappe(h)
        if trouve:
            plat, n = trouve
            return (nom, plat,
                    f"{n} entrées — À RELIRE avant d'inscrire · \"{nom}\": [\"{plat}\", \"{h}\"]",
                    f"https://{h}")

    tiers = domaines_tiers(html, urllib.parse.urlsplit(finale).netloc)
    reste = "aucune empreinte connue" + (f" · appelle : {', '.join(tiers)}" if tiers else "")
    return nom, None, reste, finale


# --- second temps : frapper directement aux portes qu'on sait ouvrir ----------
# Lire la page ne suffit pas quand elle est rendue en JavaScript : le nom de l'ATS n'est
# nulle part dans le HTML servi. Mais on connaît neuf points d'entrée par cœur — autant
# les essayer sur les sous-domaines plausibles.
#
# Ce que ça rend est une PISTE, pas une conclusion : /rss existe aussi chez ceux qui
# publient un blog. Deezer a répondu 12 « offres » qui étaient des articles sur Post
# Malone. On relit trois entrées réelles avant d'écrire la ligne du registre, toujours.
PORTES = [
    ("jibe",       "https://{h}/api/jobs?limit=2",            lambda d: len(d.get("jobs") or [])),
    ("teamtailor", "https://{h}/jobs.json",                   lambda d: len(d.get("items") or [])),
    ("recruitee",  "https://{h}/api/offers/",                 lambda d: len(d.get("offers") or [])),
    ("ashby",      "https://{h}/api/non-user-graphql",        None),
    ("smartrecruiters", "https://api.smartrecruiters.com/v1/companies/{h}/postings?limit=1",
                                                              lambda d: d.get("totalFound") or 0),
]
FLUX = [("radancy", "https://{h}/rss"), ("talentsoft", "https://{h}/handlers/offerRss.ashx?LCID=1036&top=5")]


def _json(url):
    req = urllib.request.Request(url, headers={**ENTETES, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def frappe(hote):
    """Essaie les points d'entrée connus sur un hôte. Rend (plateforme, compte) ou None."""
    for plat, gabarit, compte in PORTES:
        if compte is None:
            continue
        try:
            n = compte(_json(gabarit.format(h=hote)))
        except Exception:
            continue
        if n:
            return plat, n
    for plat, gabarit in FLUX:
        try:
            req = urllib.request.Request(gabarit.format(h=hote), headers=ENTETES)
            with urllib.request.urlopen(req, timeout=15) as r:
                n = len(ET.fromstring(r.read()).findall(".//item"))
        except Exception:
            continue
        if n:
            return plat, n
    return None


def hotes_plausibles(nom, url):
    bits = urllib.parse.urlsplit(url if "//" in url else "https://" + url)
    hote = bits.netloc
    if not hote:
        return []
    bouts = hote.split(".")
    racine = ".".join(bouts[-3:]) if hote.endswith((".gouv.fr", ".co.uk")) else ".".join(bouts[-2:])
    return list(dict.fromkeys([hote] + [f"{p}.{racine}" for p in PREFIXES]))


def cibles_par_defaut():
    txt = DATA.read_text()
    d = json.loads(txt[txt.index("const DATA = ") + 13: txt.rindex("}") + 1])
    hors = {_cle(x) for x in d.get("branchees", []) + d.get("ecartees", [])}
    hors |= {_cle(x) for x in (d.get("agregateurs") or {})}
    return [(e["nom"], e["url"]) for e in d["entreprises"]
            if e.get("url") and _cle(e["nom"]) not in hors]


def main():
    voulus = sys.argv[1:]
    cibles = cibles_par_defaut()
    if voulus:
        cherche = {_cle(v) for v in voulus}
        cibles = [c for c in cibles if _cle(c[0]) in cherche]
    if not cibles:
        return print("Rien à sonder.")

    print(f"{len(cibles)} pages carrière à lire…\n", flush=True)
    resultats = []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for nom, ats, quoi, ou in ex.map(lambda c: sonde(*c), cibles):
            resultats.append((nom, ats, quoi, ou))
            marque = "✓" if ats else "·"
            print(f"  {marque} {nom:<26} {ats or quoi}", flush=True)
            if ats:
                print(f"{'':>30} {quoi}\n{'':>30} {ou[:100]}", flush=True)

    trouves = [r for r in resultats if r[1]]
    print(f"\n{len(trouves)} / {len(resultats)} ATS identifiés\n")
    par_ats = {}
    for nom, ats, quoi, _ in trouves:
        par_ats.setdefault((ats, quoi), []).append(nom)
    for (ats, quoi), noms in sorted(par_ats.items(), key=lambda x: -len(x[1])):
        print(f"  {ats:<16} {len(noms):>2} · {quoi}")
        print(f"{'':>18} {', '.join(noms)}")


if __name__ == "__main__":
    main()
