#!/usr/bin/env python3
"""Sert la page et enregistre ce qu'on y décide.

Le navigateur ne peut pas écrire sur le disque : c'est ce serveur qui le fait.
data.js reste la source de vérité unique — on le relit, on le modifie, on le réécrit.
"""
import http.server, json, socketserver, pathlib, sys, threading, time, datetime

RACINE = pathlib.Path(__file__).resolve().parent
DATA = RACINE / "data.js"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4612
PREFIXE = "const DATA = "
STATUTS = {"a-voir", "a-postuler", "postule", "jete", "entretien", "refus", "mort"}

# Les statuts qui veulent dire « j'ai postulé ». Le premier passage par l'un d'eux grave
# `postule_le`, et plus rien ne l'écrase : sans ça, décrocher un entretien effacerait la
# date de candidature — donc le compteur « postulé il y a N jours » du suivi.
A_POSTULE = {"postule", "entretien", "refus"}

# Les notes d'un appel tiennent en quelques paragraphes. Le plafond existe pour qu'une
# page qui déraille ne puisse pas gonfler data.js indéfiniment, pas pour te brider.
NOTES_MAX = 20_000

# La page envoie un signe de vie ; sans nouvelles, le serveur s'arrête seul.
SILENCE_MAX = 120
_vu = {"t": None}
_verrou = threading.Lock()


def lire():
    """Extrait le JSON de data.js. Le fichier garde ses commentaires en tête."""
    if not DATA.exists():                       # même filet que dans sites-carriere.py
        exemple = RACINE / "data.exemple.js"
        if not exemple.exists():
            raise SystemExit(f"Ni {DATA.name}, ni {exemple.name}.")
        print(f"Pas de {DATA.name} : on part de {exemple.name}.")
        DATA.write_text(exemple.read_text())
    txt = DATA.read_text()
    i = txt.index(PREFIXE) + len(PREFIXE)
    j = txt.rindex("}") + 1
    return txt[:i], json.loads(txt[i:j]), txt[j:]


def ecrire(entete, obj, queue):
    DATA.write_text(entete + json.dumps(obj, ensure_ascii=False, indent=2) + queue)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(RACINE), **kw)

    def log_message(self, *a):
        pass

    def end_headers(self):
        """Interdire le cache, sur tout ce qui sort d'ici.

        data.js change à chaque passe de collecte ET à chaque changement de statut. Chrome,
        lui, le garde et le ressert : la page affichait 402 offres quand le disque en avait
        403. On voit alors une collecte « qui n'a rien trouvé », et on trie une liste
        périmée. Trois fichiers servis en local ne gagnent rien à être mis en cache."""
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

    def do_GET(self):
        if self.path == "/vivant":
            _vu["t"] = time.time()
            return self._json(200, {"ok": True})
        super().do_GET()

    def do_POST(self):
        if self.path == "/fiche":
            return self.fiche()
        if self.path != "/statut":
            return self.send_error(404)
        corps = self._corps(8192)     # un changement de statut tient en trois champs
        if corps is None:
            return

        oid, statut = corps.get("id"), corps.get("statut")
        if statut not in STATUTS:
            return self._json(400, {"erreur": f"statut inconnu : {statut}"})

        with _verrou:
            entete, obj, queue = lire()
            cible = next((o for o in obj.get("offres", []) if o.get("id") == oid), None)
            if cible is None:
                return self._json(404, {"erreur": f"offre inconnue : {oid}"})
            cible["statut"] = statut
            maintenant = datetime.datetime.now()
            cible["maj"] = maintenant.strftime("%Y-%m-%d")
            if statut in A_POSTULE and not cible.get("postule_le"):
                cible["postule_le"] = maintenant.strftime("%Y-%m-%d")
            # l'heure exacte, pour pouvoir relire les offres cachées dans l'ordre où elles
            # l'ont été — et rattraper celle qu'on vient de jeter par erreur
            cible["change_a"] = maintenant.isoformat(timespec="seconds")
            ecrire(entete, obj, queue)
        self._json(200, {"id": oid, "statut": statut, "maj": cible["maj"],
                         "postule_le": cible.get("postule_le")})

    def fiche(self):
        """Ce qu'on apprend sur une offre en dehors de son statut : les notes prises
        pendant un appel, et la prochaine échéance. Le statut a sa route à lui parce
        qu'il est contraint à une liste ; ici c'est du texte libre, d'où le plafond
        plus haut et la troncature plutôt qu'un refus."""
        corps = self._corps(NOTES_MAX + 4096)
        if corps is None:
            return
        oid = corps.get("id")
        with _verrou:
            entete, obj, queue = lire()
            cible = next((o for o in obj.get("offres", []) if o.get("id") == oid), None)
            if cible is None:
                return self._json(404, {"erreur": f"offre inconnue : {oid}"})
            for champ, plafond in (("notes", NOTES_MAX), ("rdv", 40), ("rdv_quoi", 120)):
                if champ in corps:
                    valeur = str(corps[champ] or "")[:plafond]
                    if valeur:
                        cible[champ] = valeur
                    else:
                        cible.pop(champ, None)      # vider un champ, c'est le retirer
            cible["maj"] = datetime.datetime.now().strftime("%Y-%m-%d")
            ecrire(entete, obj, queue)
        self._json(200, {k: cible.get(k) for k in ("id", "notes", "rdv", "rdv_quoi", "maj")})

    def _corps(self, plafond):
        """Lit et valide le corps JSON. Rend None après avoir déjà répondu en cas d'erreur."""
        try:
            n = int(self.headers.get("Content-Length", 0))
        except ValueError:
            self._json(400, {"erreur": "en-tête illisible"}); return None
        if not n:
            self._json(400, {"erreur": "corps vide"}); return None
        if n > plafond:
            self._json(413, {"erreur": "corps trop gros"}); return None
        try:
            return json.loads(self.rfile.read(n))
        except Exception:
            self._json(400, {"erreur": "json invalide"}); return None

    def _json(self, code, obj):
        c = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(c)))
        self.end_headers()
        self.wfile.write(c)


class Serveur(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


def veilleur(srv):
    while True:
        time.sleep(5)
        t = _vu["t"]
        if t is None:
            continue
        if time.time() - t > SILENCE_MAX:
            print("Onglet ferme, arret du serveur.")
            threading.Thread(target=srv.shutdown, daemon=True).start()
            return


if __name__ == "__main__":
    with Serveur(("127.0.0.1", PORT), Handler) as srv:
        print(f"Chasse ouverte sur http://127.0.0.1:{PORT}/")
        print("Le serveur s'arretera seul a la fermeture de l'onglet.")
        threading.Thread(target=veilleur, args=(srv,), daemon=True).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            pass
