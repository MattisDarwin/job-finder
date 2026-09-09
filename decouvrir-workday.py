#!/usr/bin/env python3
"""Trouve les identifiants Workday d'une entreprise.

Workday est l'ATS des grands groupes — CAC 40, banques, énergie, pharma. Son API est
publique comme les cinq autres, mais son adresse ne se devine pas : il faut un tenant,
un numéro de cluster (wd1, wd3, wd5...) et un chemin de site (« SanofiCareers »).

L'astuce est dans la forme des erreurs :
  404 « not found: Job_Posting_Site_ID=X » → tenant et cluster BONS, chemin faux
  422 vide                                → tenant ou cluster faux
Le 404 sert donc de sonde : on trouve d'abord le cluster, puis on essaie les chemins
usuels sur ce seul cluster. Deux temps, une vingtaine de requêtes par entreprise.

Usage : python3 decouvrir-workday.py [nom ...]      (sans argument : la liste intégrée)
"""
import json, sys, time, urllib.request, urllib.error, concurrent.futures as cf

# Vus en vrai : Banque de France est sur wd103, Salesforce sur wd12, Otis sur wd504.
CLUSTERS = ["wd1", "wd3", "wd5", "wd2", "wd103", "wd12", "wd101", "wd102", "wd105",
            "wd10", "wd504", "wd501", "wd104", "wd108"]
CORPS = json.dumps({"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}).encode()


def _post(tenant, cluster, site, essais=2):
    """Retourne (statut, données). Statut : 'ok', 'site-faux', 'non'.

    Une requête sur soixante tombe sans raison. Sans seconde tentative, l'entreprise est
    déclarée injoignable alors qu'elle répond — Airbus et Valeo sont passées à travers en
    lot mais ont été trouvées seules. Seules les pannes réseau sont retentées : un 404 ou
    un 422 est une réponse, pas un échec.
    """
    url = f"https://{tenant}.{cluster}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    for essai in range(essais):
        req = urllib.request.Request(url, data=CORPS, method="POST", headers={
            "Content-Type": "application/json", "Accept": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"})
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                return "ok", json.loads(r.read())
        except urllib.error.HTTPError as e:
            corps = e.read().decode("utf-8", "replace")
            return ("site-faux" if "Job_Posting_Site_ID" in corps else "non"), None
        except Exception:
            if essai + 1 == essais:
                return "non", None
            time.sleep(0.6)


def cluster_de(tenant):
    """Premier temps : quel cluster héberge ce tenant ? Le 404 le trahit."""
    for c in CLUSTERS:
        etat, _ = _post(tenant, c, "ZzSondeInexistante")
        if etat in ("site-faux", "ok"):
            return c
    return None


def chemins(tenant, nom=""):
    """Les noms de site que Workday voit passer le plus souvent.

    Il n'y a pas de règle : chaque entreprise nomme le sien comme elle veut. La liste
    s'allonge à mesure qu'on en croise. Un cluster trouvé sans chemin (« ~ » à l'écran)
    veut dire qu'il manque un motif ici — l'ajouter plutôt que de saisir l'entrée à la main.

    Le chemin dérive du NOM de l'entreprise autant que du tenant, et les deux diffèrent
    souvent : Airbus loue le tenant « ag » mais son site s'appelle « /Airbus ».
    """
    formes = []
    for base in dict.fromkeys([tenant, "".join(c for c in nom.lower() if c.isalnum())]):
        if base:
            formes += _motifs(base)
    return list(dict.fromkeys(formes))


def _motifs(tenant):
    T, U = tenant.capitalize(), tenant.upper()
    return [f"{T}Careers", "Careers", "External", f"{T}_Careers", f"{T}_External_Career_Site",
            "External_Career_Site", f"{T}careers", tenant, T, U, "CareerSite", "Career_Site",
            "GlobalCareers", "Global_Careers", f"{T}JobBoard", "Jobs", "careers", "jobs",
            f"{T}_Careers_External", "ExternalCareerSite", f"{T}External", f"{T}_External",
            f"{tenant}-ext", f"{T}-ext", f"{tenant}_ext", f"{T}Ext", "ext", "Ext",
            f"{tenant}_careers", f"{tenant}Careers", f"{U}_Careers", f"{U}Careers",
            "External_Careers", "ExternalCareers", "External_Site", "ExternalSite",
            "Professional", "Professionals", "ExperiencedProfessionals", "Experienced",
            "Global", "GlobalExternal", "Recruiting", "Recruitment", f"{T}_Recruiting",
            f"{T}_Global_Careers", f"{T}_Jobs", f"{T}Jobs", "careersite", "CareerHub",
            f"{T}_Career_Site", f"{T}_CareerSite", "Search", "SearchJobs", f"{T}_Talent",
            "career", "Career", "Ext_Career_Site", "ExtCareerSite", f"{T}careersite",
            f"{T}CareerSite", f"{tenant}careersite", "Ext", "EXT", f"{T}_Ext",
            f"{T}_Career", f"{T}Career", f"{tenant}_career", "External_Career_Site_ID01",
            "ABBcareers", f"{T}_careers", f"{U}_EXTERNAL", "External_Career_Site_ID02"]


# Le tenant n'est presque jamais le nom de l'entreprise : Airbus loue « ag », Michelin
# « michelinhr ». Aucune règle — ces alias se découvrent un par un et s'ajoutent ici.
ALIAS = {"airbus": "ag", "michelin": "michelinhr", "totalenergies": "total",
         "saintgobain": "saint-gobain", "societegenerale": "socgen",
         "creditagricole": "ca", "philipmorris": "pmi", "kuehnenagel": "kuehne-nagel",
         "swissre": "swissre", "barrycallebaut": "barry-callebaut"}


def trouve(nom):
    """Le nom peut forcer son tenant : « Airbus=ag »."""
    if "=" in nom:
        nom, tenant = nom.split("=", 1)
    else:
        base = "".join(ch for ch in nom.lower() if ch.isalnum())
        tenant = ALIAS.get(base, base)
    c = cluster_de(tenant)
    if not c:
        return nom, None
    for site in chemins(tenant, nom):
        etat, d = _post(tenant, c, site)
        if etat == "ok":
            return nom, (c, site, d.get("total") or 0, tenant)
    return nom, ("cluster-seul", c, 0, tenant)


LISTE = ["Sanofi", "Novartis", "Roche", "Danone", "Loreal", "Schneider", "Capgemini",
         "Alstom", "Michelin", "Pernod", "Publicis", "Kering", "Essilor", "Legrand",
         "Vinci", "Bouygues", "Orange", "Engie", "Veolia", "Saint-Gobain", "Thales",
         "Safran", "Airbus", "Renault", "Stellantis", "Valeo", "Faurecia", "Arkema",
         "Air Liquide", "Total", "TotalEnergies", "BNP Paribas", "Societe Generale",
         "Credit Agricole", "AXA", "Amundi", "Natixis", "Carrefour", "Auchan", "Decathlon",
         "LVMH", "Hermes", "Sodexo", "Elior", "Ubisoft", "Dassault", "Atos", "Sopra",
         "Worldline", "Edenred", "Teleperformance", "Nexans", "Eiffage", "SEB",
         "Nestle", "Nespresso", "ABB", "Sika", "Givaudan", "Lonza", "Adecco", "Zurich",
         "Swiss Re", "UBS", "Julius Baer", "Richemont", "Logitech", "Barry Callebaut",
         "Straumann", "Alcon", "Sonova", "Geberit", "Holcim", "Clariant", "Firmenich",
         "Philip Morris", "Syngenta", "Bobst", "Swatch", "Kuehne Nagel", "Garmin"]

if __name__ == "__main__":
    noms = sys.argv[1:] or LISTE
    print(f"{len(noms)} entreprises × 10 clusters, puis les chemins usuels…\n", flush=True)
    trouves, partiels = [], []
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        for nom, r in ex.map(trouve, noms):
            if not r:
                continue
            if r[0] == "cluster-seul":
                partiels.append((nom, r[1], r[3])); print(f"  ~ {nom:<20} {r[3]}.{r[1]} — chemin introuvable", flush=True)
            else:
                trouves.append((nom, *r)); print(f"  ✓ {nom:<20} {r[0]}/{r[1]}  ({r[2]} offres)", flush=True)

    print(f"\n{len(trouves)} joignables · {sum(t[3] for t in trouves)} offres\n")
    for nom, c, site, n, tenant in sorted(trouves, key=lambda t: -t[3]):
        print(f'    "{nom}": ["workday", "{tenant}/{c}/{site}"],   // {n} offres')
    if partiels:
        print("\n  Cluster trouvé mais chemin inconnu — à compléter à la main :")
        for nom, c, tenant in partiels:
            print(f"    {nom} → https://{tenant}.{c}.myworkdayjobs.com/")
