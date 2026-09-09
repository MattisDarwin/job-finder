#!/usr/bin/env python3
"""Cherche ce que les offres jetées ont en commun, et que les gardées n'ont pas.

Le filtre de `sites-carriere.py` est écrit à la main. Ce script ne le modifie pas : il
lit les décisions de tri déjà prises et propose des mots à ajouter, avec leurs comptes.
C'est à toi de trancher — un mot mal choisi coûte des offres qu'on ne verra jamais.

Il devient utile avec le volume. Sous SEUIL_FIABLE offres jetées, il le dit et se tait
plutôt que de tirer des conclusions d'un échantillon trop maigre.

Usage : python3 apprendre.py [--tout]     (--tout : montrer aussi les signaux faibles)
"""
import collections, json, pathlib, re, sys, unicodedata, importlib.util

RACINE = pathlib.Path(__file__).resolve().parent
CACHES = {"jete", "mort"}
SEUIL_FIABLE = 60        # en dessous, aucun motif ne mérite qu'on modifie le filtre
MIN_OCCURRENCES = 3      # un mot vu deux fois est un hasard
FACTEUR = 3.0            # combien de fois plus fréquent chez les jetées que chez les gardées

VIDES = {"de", "du", "des", "la", "le", "les", "et", "en", "un", "une", "pour", "chez",
         "of", "the", "and", "for", "to", "in", "at", "with", "cdi", "cdd", "senior",
         "junior", "confirme", "experimente", "expérimenté", "manager", "chef", "projet",
         "responsable", "charge", "chargé", "specialist", "specialiste", "spécialiste"}


def mots(titre):
    """Mots et paires de mots, sans accents ni ponctuation."""
    t = unicodedata.normalize("NFKD", titre.lower()).encode("ascii", "ignore").decode()
    bruts = [w for w in re.findall(r"[a-z0-9]{3,}", t) if w not in VIDES]
    return set(bruts) | {f"{a} {b}" for a, b in zip(bruts, bruts[1:])}


def charger():
    s = (RACINE / "data.js").read_text()
    i, j = s.index("const DATA = ") + 13, s.rindex("}") + 1
    return json.loads(s[i:j])["offres"]


def main():
    tout = "--tout" in sys.argv
    offres = charger()
    jetees = [o for o in offres if o.get("statut") in CACHES]
    gardees = [o for o in offres if o.get("statut") not in CACHES]
    if not jetees:
        return print("Aucune offre jetée : rien à apprendre.")

    # ce que le filtre attrape déjà n'a pas besoin d'être proposé
    sp = importlib.util.spec_from_file_location("sc", RACINE / "sites-carriere.py")
    sc = importlib.util.module_from_spec(sp); sp.loader.exec_module(sc)
    reste = [o for o in jetees if sc.pertinent(o["poste"], o["lieu"])]

    print(f"{len(jetees)} offres jetées · {len(gardees)} gardées")
    print(f"{len(jetees) - len(reste)} sont déjà rattrapées par le filtre actuel ;"
          f" le signal est dans les {len(reste)} autres.\n")
    if not reste:
        return print("Tout ce qui a été jeté serait déjà écarté aujourd'hui. Rien à ajouter.")

    cj, cg = collections.Counter(), collections.Counter()
    for o in reste:
        cj.update(mots(o["poste"]))
    for o in gardees:
        cg.update(mots(o["poste"]))

    seuil = 1 if tout else MIN_OCCURRENCES
    pistes = []
    for mot, n in cj.items():
        taux_j = n / len(reste)
        taux_g = cg[mot] / max(1, len(gardees))
        if n >= seuil and taux_j >= FACTEUR * taux_g:
            pistes.append((n, cg[mot], mot))

    if len(jetees) < SEUIL_FIABLE:
        print(f"⚠ Échantillon trop petit ({len(jetees)} jetées, il en faudrait {SEUIL_FIABLE}).")
        print("  Ce qui suit est indicatif : à lire, pas à appliquer les yeux fermés.\n")
    if not pistes:
        return print("Aucun mot ne ressort. Continue à trier, repasse plus tard.")

    print(f"{'jetées':>7} {'gardées':>8}   mot")
    for n, g, mot in sorted(pistes, reverse=True)[:25]:
        print(f"{n:>7} {g:>8}   {mot}")
        for o in [x for x in reste if mot in mots(x['poste'])][:2]:
            print(f"{'':>16}   · {o['entreprise'][:14]} — {o['poste'][:56]}")


if __name__ == "__main__":
    main()
