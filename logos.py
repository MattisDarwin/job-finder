#!/usr/bin/env python3
"""Récupère une fois pour toutes l'icône de chaque entreprise, et l'écrit dans logos.js.

Pourquoi hors ligne. La page pourrait pointer vers un service d'icônes (Google, Clearbit,
DuckDuckGo) en une ligne — mais alors chaque ouverture de la page annonce à un tiers la
liste des entreprises regardées, et la page ne marche plus sans réseau. On récupère donc
l'icône ici, une fois, et on la range en base64 dans un fichier servi en local.

Ce n'est pas indispensable : sans logo, la page dessine un monogramme. Ce script ne fait
qu'améliorer ce qui marche déjà, et une entreprise qu'il rate ne casse rien.

Usage : python3 logos.py [--tout]
  sans argument : ne cherche que les entreprises qui n'ont pas encore d'icône
  --tout        : refait tout le monde
"""
import base64
import collections
import concurrent.futures as cf
import json
import pathlib
import re
import sys
import unicodedata
import urllib.parse
import urllib.request

RACINE = pathlib.Path(__file__).resolve().parent
DATA, SORTIE = RACINE / "data.js", RACINE / "logos.js"
PREFIXE_LOGOS = "const LOGOS = "

# Au-delà, ce n'est plus une icône : on laisse le monogramme faire son travail plutôt que
# d'alourdir la page. 24 Ko de base64 ≈ 18 Ko d'image, large pour un favicon.
POIDS_MAX = 24_000
ENTETES = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
           "Accept": "image/avif,image/webp,image/png,image/*,*/*;q=0.8"}

# Les signatures des formats qu'un navigateur affichera sans discuter. Le type annoncé par
# le serveur ment trop souvent (« text/plain » pour un PNG) : on lit les premiers octets.
SIGNATURES = [(b"\x89PNG\r\n\x1a\n", "image/png"), (b"GIF8", "image/gif"),
              (b"\xff\xd8\xff", "image/jpeg"), (b"\x00\x00\x01\x00", "image/x-icon"),
              (b"RIFF", "image/webp")]


def _cle(nom):
    """La même clé dépouillée que sites-carriere.py et index.html : « Roche (CH) » = « Roche »."""
    return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFKD", nom.lower())
                  .encode("ascii", "ignore").decode().replace("(ch)", ""))


def _type(octets):
    if octets[:4] == b"RIFF" and octets[8:12] != b"WEBP":
        return None
    for signature, mime in SIGNATURES:
        if octets.startswith(signature):
            return mime
    if octets.lstrip()[:5] in (b"<svg ", b"<svg>", b"<?xml"):
        return "image/svg+xml"
    return None


def _lire(url, taille_max=POIDS_MAX * 2):
    req = urllib.request.Request(url, headers=ENTETES)
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read(taille_max + 1), r.geturl()


def _candidates(url_site):
    """Les adresses où une icône se cache, de la plus sûre à la plus spéculative.

    Beaucoup de groupes servent leur site carrière sur un sous-domaine sans favicon
    (`jobs.example.com`) alors que le domaine principal en a un : on essaie les deux."""
    bits = urllib.parse.urlsplit(url_site if "//" in url_site else "https://" + url_site)
    hote = bits.netloc
    if not hote:
        return [], []
    racine = ".".join(hote.split(".")[-2:]) if hote.count(".") >= 2 else hote
    hotes = list(dict.fromkeys([hote, racine, "www." + racine]))
    return [f"https://{h}/favicon.ico" for h in hotes], hotes


LIEN_ICONE = re.compile(
    r"""<link[^>]+rel\s*=\s*["'][^"']*\bicon\b[^"']*["'][^>]*>""", re.I)
HREF = re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I)


def _dans_la_page(hote):
    """Second recours : lire le <head> et y trouver le <link rel="icon">."""
    try:
        html, finale = _lire(f"https://{hote}/", 200_000)
    except Exception:
        return []
    tete = html[:200_000].decode("utf-8", "replace")
    urls = []
    for balise in LIEN_ICONE.findall(tete):
        m = HREF.search(balise)
        if m:
            urls.append(urllib.parse.urljoin(finale, m.group(1)))
    return urls


def icone(nom, url_site):
    """Retourne (nom, data-URI) ou (nom, None). Ne lève jamais : un raté n'est pas une panne."""
    try:
        directes, hotes = _candidates(url_site)
    except Exception:
        return nom, None
    essais = list(directes)
    for h in hotes[:2]:
        essais += _dans_la_page(h)
    vus = set()
    for u in essais:
        if u in vus:
            continue
        vus.add(u)
        try:
            octets, _ = _lire(u)
        except Exception:
            continue
        mime = _type(octets)
        if not mime or len(octets) > POIDS_MAX:
            continue
        return nom, f"data:{mime};base64," + base64.b64encode(octets).decode()
    return nom, None


# Un site carrière hébergé par un ATS sert le favicon de l'ATS, pas celui de l'entreprise :
# les seize sociétés sur Ashby renvoyaient toutes le même losange. Une icône identique chez
# trois entreprises ou plus n'appartient donc à aucune — on la jette, le monogramme est
# plus juste. Deux, en revanche, peuvent légitimement partager : Indeed France et Suisse.
PARTAGE_MAX = 2


def sans_icones_de_plateforme(logos):
    compte = collections.Counter(logos.values())
    gardes = {k: v for k, v in logos.items() if compte[v] <= PARTAGE_MAX}
    jetees = len(logos) - len(gardes)
    if jetees:
        print(f"  ({jetees} icônes écartées : c'était celle de la plateforme, pas de l'entreprise)")
    return gardes


def charger_data():
    txt = DATA.read_text()
    i = txt.index("const DATA = ") + len("const DATA = ")
    return json.loads(txt[i:txt.rindex("}") + 1])


def charger_logos():
    if not SORTIE.exists():
        return {}
    txt = SORTIE.read_text()
    i = txt.index(PREFIXE_LOGOS) + len(PREFIXE_LOGOS)
    return json.loads(txt[i:txt.rindex("}") + 1])


def main():
    tout = "--tout" in sys.argv
    obj = charger_data()
    deja = {} if tout else charger_logos()
    cibles = {}
    for e in obj.get("entreprises", []):
        k = _cle(e["nom"])
        if e.get("url") and k not in deja:
            cibles[k] = (e["nom"], e["url"])

    trouves = dict(deja)
    if cibles:
        print(f"{len(cibles)} entreprises à sonder ({len(deja)} déjà connues)…\n")
        with cf.ThreadPoolExecutor(max_workers=12) as ex:
            for k, (nom, uri) in zip(cibles, ex.map(
                    lambda kv: icone(*kv[1]), cibles.items())):
                if uri:
                    trouves[k] = uri
                    print(f"  ✓ {nom:<26} {len(uri)//1024} Ko")
                else:
                    print(f"  · {nom:<26} pas d'icône — monogramme")
    else:
        print(f"{len(deja)} icônes déjà là, rien de nouveau à sonder.")

    trouves = sans_icones_de_plateforme(trouves)
    ordonne = {k: trouves[k] for k in sorted(trouves)}
    SORTIE.write_text(
        "// Icônes des entreprises, récupérées une fois par logos.py et rangées ici en\n"
        "// base64 : la page reste hors ligne et n'annonce à personne ce qu'on regarde.\n"
        "// Une entreprise absente de ce fichier reçoit un monogramme dessiné en CSS.\n"
        "// Régénérer : python3 logos.py [--tout]\n"
        + PREFIXE_LOGOS + json.dumps(ordonne, ensure_ascii=False, indent=1) + ";\n")
    poids = SORTIE.stat().st_size / 1024
    print(f"\n{len(ordonne)} icônes · logos.js fait {poids:.0f} Ko")


if __name__ == "__main__":
    main()
