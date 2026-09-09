#!/usr/bin/env python3
"""Teste des noms d'entreprises contre les API publiques des plateformes de recrutement.

Usage : python3 decouvrir.py [fichier-de-noms]
Sans argument, utilise la liste intégrée. Affiche qui est joignable et sur quelle
plateforme, prêt à coller dans sites-carriere.json.
"""
import json, sys, urllib.request, concurrent.futures as cf

LISTE = """
doctolib qonto alan payfit contentsquare dataiku ledger blablacar swile backmarket mirakl
algolia sorare deezer accor ubisoft criteo malt spendesk pennylane lucca aircall younited
shine luko pigment ankorstore vestiairecollective veepee manomano leboncoin getaround
ornikar wandercraft exotec verkor innovafeed ynsect ledger sunday lydia agicap
qonto-fr matera hiflow jow frichti cajoo gorillas flink dott cowboy voi tier
alma silvr defacto karmen unlimitd toucan choose upflow libeo agicap regate
mooncard spendesk qonto memo-bank margo shift-technology owkin cardiologs therapixel
implicity nabla posos synapse-medicine lifen honestica maiia keldoc qare livi
360learning coorpacademy openclassrooms edflex unow rise-up beedeez teach-on-mars
lucca payfit personio factorial combo skello snapshift staffme brigad side
mano-mano cdiscount fnac-darty rakuten-france showroomprive laredoute sarenza spartoo
believe deezer sacem qobuz molotov salto dailymotion brut konbini
sncf-connect trainline flixbus ouigo blablabus getaround virtuo marcel g7
younited-credit finfrog cashbee yomoni nalo goodvest ramify sapians
ivalua akeneo talend jahia sinequa systran quantmetry artefact ekimetrics onepoint
sopra-steria capgemini atos devoteam wavestone sia-partners keyrus micropole
swile edenred sodexo elior compass-group
nestle roche novartis lonza givaudan sika logitech nexthink scandit sonarsource
frontify smallpdf beekeeper avaloq temenos six-group swissquote selise ergon
proton wefox flatfox getyourguide sherpany
mistral-ai hugging-face poolside adaptive-ml dust photoroom finegrain giskard
"""

def apis(c):
    return [
        ("greenhouse", f"https://boards-api.greenhouse.io/v1/boards/{c}/jobs",
         lambda d: len(d.get("jobs", []))),
        ("lever", f"https://api.lever.co/v0/postings/{c}?mode=json",
         lambda d: len(d) if isinstance(d, list) else 0),
        ("smartrecruiters", f"https://api.smartrecruiters.com/v1/companies/{c}/postings?limit=1",
         lambda d: d.get("totalFound", 0)),
        ("ashby", f"https://api.ashbyhq.com/posting-api/job-board/{c}",
         lambda d: len(d.get("jobs", []))),
        ("recruitee", f"https://{c}.recruitee.com/api/offers/",
         lambda d: len(d.get("offers", []))),
    ]

def essai(t):
    nom, plat, url, compte = t
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            n = compte(json.loads(r.read()))
        return (nom, plat, n) if n else None
    except Exception:
        return None

noms = (open(sys.argv[1]).read() if len(sys.argv) > 1 else LISTE).split()
noms = sorted(set(noms))
taches = [(c, p, u, f) for c in noms for p, u, f in apis(c)]
print(f"{len(noms)} noms × 5 plateformes = {len(taches)} essais…\n", file=sys.stderr)

trouves = {}
with cf.ThreadPoolExecutor(max_workers=48) as ex:
    for r in ex.map(essai, taches):
        if r and r[2] > trouves.get(r[0], (None, 0))[1]:
            trouves[r[0]] = (r[1], r[2])

items = sorted(trouves.items(), key=lambda x: -x[1][1])
print(f"{len(items)} entreprises joignables · {sum(v[1] for _, v in items)} offres\n")
for nom, (plat, n) in items:
    print(f'    "{nom}": ["{plat}", "{nom}"],   // {n} offres')
