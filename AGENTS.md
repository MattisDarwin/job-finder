# job-finder — guide pour l'agent

Format [AGENTS.md](https://agents.md/). `CLAUDE.md` en est un lien symbolique.

Ce dépôt n'est pas une application finie : c'est une **charpente faite pour être modifiée**,
et vous êtes probablement l'agent qui va la modifier. Ce fichier dit quoi changer, où, et
selon quelles règles.

## En trois phrases

`sites-carriere.py` interroge les API publiques des plateformes de recrutement et verse
les offres qui passent le filtre. `data.js` est la **source de vérité unique** — lue par
la page, écrite par `serveur.py`, parce qu'un navigateur ne peut pas écrire sur le disque.
`profil.json` décide de ce qui entre : c'est le fichier de l'utilisateur, pas le vôtre.

## Les quatre règles à ne pas casser

1. **Aucune dépendance** hors bibliothèque standard Python. C'est délibéré : l'outil doit
   marcher sur une machine neuve avec un `git clone` et rien d'autre.
2. **Une offre déjà triée ne se modifie ni ne se supprime jamais.** Un statut est une
   décision humaine. `postule_le` en particulier se grave une fois et ne se réécrit pas.
3. **Toute modification du filtre se teste dans les deux sens** — ce qui passe et ce qui
   tombe — avant d'être appliquée. Un filtre qui écarte tout « marche » aussi bien qu'un
   filtre qui garde tout.
4. **On ne candidate jamais, on n'envoie rien.** L'outil trie ; l'humain postule.

## Ce que vous aurez à faire, et comment

### Régler le profil

Tout est dans `profil.json` : `garde`, `ecarte`, `lieux`, `langues_ecartees`. Des
expressions régulières, comparées sans tenir compte de la casse, jointes par `|`.

Deux pièges qui coûtent cher :

- **Écrivez des limites de mots.** `\bai\b` attrape « AI Manager » mais pas « Certain ».
  Sans les `\b`, la moitié de la liste devient du bruit.
- **`ecarte` gagne toujours contre `garde`**, il est évalué en premier. Si vous ajoutez
  `op[ée]rationnel` au rejet, vous annulez « excellence opérationnelle » du côté gardé,
  sans qu'aucune erreur ne le signale.

Pour mesurer un changement, comparez les jetées à ce que l'utilisateur a **activement
retenu**, jamais à « tout ce qui n'est pas jeté » : une offre non triée n'est pas une
offre acceptée. C'est l'erreur qui fait croire à des faux positifs qui n'existent pas.

### Ajouter une entreprise

Une ligne dans `sites-carriere.json` :

```json
"Doctolib": { "plateforme": "greenhouse", "id": "doctolib", "tags": ["tech", "sante"] }
```

Pour trouver la plateforme : `python3 decouvrir-ats.py "Nom"`. Il part de l'adresse du
site carrière et lit ce qu'elle sert vraiment.

**Vérifiez toujours sur trois offres réelles avant d'inscrire la ligne.** Un identifiant
libre est premier arrivé, premier servi : `decouvrir.py` a déjà proposé « vinci » sur
Ashby, qui est une startup de Palo Alto, et un `/rss` qui rendait douze articles de blog
présentés comme des offres. Un nom qui correspond ne prouve rien.

### Écrire une plateforme qui manque

Le motif est toujours le même : **une fonction qui prend un identifiant et rend une liste
de tuples `(titre, lieu, url, date)`**. Puis une entrée dans le dictionnaire `PLATEFORMES`.
Regardez `greenhouse()` pour le cas simple, `workday()` pour un cas difficile.

Trois choses apprises en écrivant les onze existantes :

- **Un `User-Agent` tronqué se fait rendre 403** par certains pare-feux applicatifs.
  Annoncez un vrai navigateur — la constante `NAVIGATEUR` est là pour ça.
- **« L'URL répond 200 » ne veut pas dire « l'offre est lisible ».** Certaines plateformes
  rendent 200 sur une page de candidature entièrement vide. Ouvrez-en une pour de vrai.
- **Une pagination peut être ignorée en silence.** Un site rendait éternellement la
  première page sans lever d'erreur : 800 offres lues pour 200 distinctes. Comptez les
  identifiants distincts, pas les réponses.

### Toucher à la page

`index.html` est un seul fichier, sans framework et sans build. Le CSS est en haut, le JS
en bas. Trois piles, et une offre n'est jamais dans deux à la fois : le **tri** (ce qui
attend une décision), le **rebut** (jeté avant de postuler), le **suivi** (ce à quoi on a
postulé — c'est `postule_le` qui range là, pas le statut courant).

Les animations n'animent qu'`opacity` et `transform`, ne dépassent pas 220 ms, et une
carte n'entre en scène qu'une fois : sans ça, chaque clic rejoue l'animation des centaines
d'autres.

## Le français partout

Noms de variables, commentaires, messages, noms de fichiers. Ce n'est pas une coquetterie :
le projet se lit comme il s'écrit, et le mélange des deux langues rend le code illisible.
Les commentaires disent **pourquoi**, pas quoi — le quoi se lit dans le code.

## Structure

```
sites-carriere.py     la collecte : onze plateformes, le filtre, l'écriture de data.js
serveur.py            sert la page, enregistre statuts et notes, s'arrête tout seul
index.html            la page : trois onglets, aucun framework
profil.json           qui vous êtes, ce que vous cherchez           (à créer, gitignoré)
sites-carriere.json   le registre : entreprise → plateforme, id, tags
data.js               la source de vérité : offres, entreprises      (à créer, gitignoré)
decouvrir-ats.py      quel ATS sert un site carrière donné
decouvrir.py          teste des identifiants contre cinq API
decouvrir-workday.py  trouve les identifiants Workday
apprendre.py          cherche des motifs dans les offres jetées
logos.py              récupère les icônes des entreprises, hors ligne
```
