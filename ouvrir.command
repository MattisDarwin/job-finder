#!/usr/bin/env bash
# Double-clic pour ouvrir job finder.
# Le serveur s'arrete seul a la fermeture de l'onglet.
cd "$(dirname "$0")"
PORT=4612
lsof -ti :$PORT 2>/dev/null | xargs kill 2>/dev/null
python3 serveur.py $PORT &
SRV=$!
sleep 1
open "http://127.0.0.1:$PORT/index.html"
trap "kill $SRV 2>/dev/null" EXIT
wait $SRV
echo; echo "Termine. Tu peux fermer cette fenetre."
