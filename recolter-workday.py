#!/usr/bin/env python3
"""Transforme des URL myworkdayjobs en entrées de registre.

Il n'existe **aucun annuaire public des tenants Workday** — c'est le point dur, reconnu
par tous ceux qui documentent cette API. `decouvrir-workday.py` devine par sondage ; ce
script fait l'inverse et c'est bien plus sûr : on part d'URL déjà vues (résultats de
recherche, offre reçue par un ami, lien LinkedIn) et on en extrait les trois identifiants.

C'est le seul moyen d'attraper ce qu'aucune règle ne produit : Renault loue le tenant
« alliancewd », Deloitte « fina », Airbus « ag ». Aucun sondage ne trouve ça.

Usage :
    python3 recolter-workday.py URL...
    pbpaste | python3 recolter-workday.py          # colle une page de résultats
"""
import concurrent.futures as cf, json, re, sys, pathlib

RACINE = pathlib.Path(__file__).resolve().parent
REGISTRE = RACINE / "sites-carriere.json"

# https://TENANT.wdN.myworkdayjobs.com[/fr-FR]/SITE/...
URL = re.compile(r"https?://([a-z0-9][a-z0-9-]*)\.(wd\d+)\.myworkdayjobs\.com"
                 r"/(?:[a-z]{2}-[A-Z]{2}/)?([^/?#\s\"']+)", re.I)
# ce qui suit le domaine n'est pas toujours le site : parfois une route de l'application
PAS_UN_SITE = {"job", "jobs", "apply", "login", "wday", "details", "search", "index.html"}


def extraire(texte):
    vus = {}
    for tenant, cluster, site in URL.findall(texte):
        if site.lower() in PAS_UN_SITE:
            continue
        vus.setdefault((tenant.lower(), cluster.lower(), site), None)
    return list(vus)


def verifie(triplet):
    import urllib.request, urllib.error
    tenant, cluster, site = triplet
    url = f"https://{tenant}.{cluster}.myworkdayjobs.com/wday/cxs/{tenant}/{site}/jobs"
    corps = json.dumps({"appliedFacets": {}, "limit": 1, "offset": 0, "searchText": ""}).encode()
    req = urllib.request.Request(url, data=corps, method="POST", headers={
        "Content-Type": "application/json", "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return triplet, json.loads(r.read()).get("total") or 0
    except Exception:
        return triplet, -1


if __name__ == "__main__":
    texte = " ".join(sys.argv[1:]) or sys.stdin.read()
    triplets = extraire(texte)
    if not triplets:
        sys.exit("Aucune URL myworkdayjobs reconnue.")
    registre = json.loads(REGISTRE.read_text())
    # les écartés comptent comme connus : on ne veut pas les reproposer à chaque récolte
    deja = {tuple(v[1].split("/"))
            for bloc in ("entreprises", "ecartes")
            for v in registre.get(bloc, {}).values() if v[0] == "workday"}
    print(f"{len(triplets)} adresses extraites, vérification…\n")
    bons = []
    with cf.ThreadPoolExecutor(max_workers=5) as ex:
        for (t, c, s), n in ex.map(verifie, triplets):
            marque = "  (déjà au registre)" if (t, c, s) in deja else ""
            if n > 0:
                bons.append((t, c, s, n)); print(f"  ✓ {t}/{c}/{s}  {n} offres{marque}")
            elif n == 0:
                print(f"  · {t}/{c}/{s}  répond mais 0 offre")
            else:
                print(f"  ✗ {t}/{c}/{s}")
    print(f"\n{len(bons)} adresses vivantes — à coller dans sites-carriere.json :\n")
    for t, c, s, n in sorted(bons, key=lambda x: -x[3]):
        if (t, c, s) not in deja:
            print(f'    "{t.capitalize()}": ["workday", "{t}/{c}/{s}"],   // {n} offres')
