# job-finder — guide pour l'agent

Format [AGENTS.md](https://agents.md/). `CLAUDE.md` en est un lien symbolique.

Ce dépôt n'est pas une application finie : c'est une **charpente faite pour être modifiée**,
et vous êtes probablement l'agent qui va la modifier. Ce fichier suffit — vous n'avez pas
besoin d'autre chose pour travailler ici.

---

## En trois phrases

`sites-carriere.py` interroge les API publiques des plateformes de recrutement et verse
les offres qui passent le filtre. `data.js` est la **source de vérité unique** — lue par
la page, écrite par `serveur.py`, parce qu'un navigateur ne peut pas écrire sur le disque.
`profil.json` décide de ce qui entre : c'est le fichier de l'utilisateur, pas le vôtre.

## Les commandes

```bash
python3 sites-carriere.py      # une passe de collecte (2 à 5 min)
python3 serveur.py 4612        # sert la page sur http://127.0.0.1:4612/
open ouvrir.command            # macOS : fait les deux d'un coup
python3 decouvrir-ats.py "X"   # sur quelle plateforme est l'entreprise X ?
python3 apprendre.py           # que reprocher aux offres jetées ?
python3 logos.py               # récupère les icônes des entreprises
```

Le serveur s'arrête seul quand l'onglet se ferme. Il n'y a rien à installer : Python 3 et
sa bibliothèque standard suffisent.

---

## La première séance : ce qu'il faut demander

Un dépôt fraîchement cloné ne sait rien de son utilisateur. **Avant d'écrire `profil.json`,
posez ces questions.** Elles sont courtes et elles décident de tout le reste.

1. **Quels intitulés de poste vises-tu ?** Demandez trois à cinq exemples d'annonces qui
   l'intéresseraient vraiment. C'est de là que sortent les motifs de `garde` — pas d'une
   description abstraite du métier.
2. **Qu'est-ce qui te ferait fermer l'annonce tout de suite ?** Les métiers voisins qu'on
   confond avec le sien, les niveaux hors d'atteinte, les domaines qui ne l'intéressent
   pas. C'est `ecarte`, et c'est **plus important que `garde`** : c'est ce qui rend la
   liste lisible.
3. **Où ? Et le télétravail compte-t-il plus que le reste ?** Villes, pays, « remote ».
4. **Quel type de contrat ?** CDI, CDD, VIE, alternance. Un VIE échappe au filtre
   géographique si `vie_partout` est vrai — c'est un poste à l'étranger par nature.
5. **Quelles entreprises te viennent en tête ?** Servez-vous en pour amorcer le registre :
   `decouvrir-ats.py` dira sur quelle plateforme elles sont.

Ensuite, **montrez-lui la première passe et taisez-vous**. Le filtre se règle sur des
offres réelles, pas sur des intentions. Vingt minutes de tri en apprennent plus que
vingt minutes de discussion.

## La boucle, ensuite

```
collecte  →  l'utilisateur trie d'un clic  →  apprendre.py  →  vous ajustez le profil
```

`apprendre.py` compare les offres jetées aux autres et propose des mots. **Il propose, il
n'applique rien** — et c'est délibéré : un mot mal choisi coûte des offres qu'on ne verra
jamais.

---

## Les quatre règles à ne pas casser

1. **Aucune dépendance** hors bibliothèque standard Python. L'outil doit marcher sur une
   machine neuve avec un `git clone` et rien d'autre.
2. **Une offre déjà triée ne se modifie ni ne se supprime jamais.** Un statut est une
   décision humaine. `postule_le` en particulier se grave une fois et ne se réécrit pas :
   c'est lui qui date la candidature dans l'onglet Suivi.
3. **Toute modification du filtre se teste dans les deux sens** — ce qui passe et ce qui
   tombe. Un filtre qui écarte tout « marche » aussi bien qu'un filtre qui garde tout.
4. **On ne candidate jamais, on n'envoie rien.** L'outil trie ; l'humain postule.

## Ce qui n'est pas à vous

Trois choses appartiennent à l'utilisateur et se **proposent**, jamais ne s'imposent :
le contenu de `profil.json`, les statuts qu'il a posés, et le choix d'ajouter ou d'écarter
une entreprise. Devant un doute de goût — faut-il écarter tel domaine ? — demandez.
Devant un fait vérifiable — cette plateforme rend-elle des offres ? — vérifiez.

---

## Régler le profil

Tout est dans `profil.json` : `garde`, `ecarte`, `lieux`, `langues_ecartees`. Des
expressions régulières, comparées sans tenir compte de la casse, jointes par `|`.

Deux pièges qui coûtent cher :

- **Écrivez des limites de mots.** `\bai\b` attrape « AI Manager » mais pas « Certain ».
  Sans les `\b`, la moitié de la liste devient du bruit.
- **`ecarte` gagne toujours contre `garde`**, il est évalué en premier. Si vous ajoutez
  `op[ée]rationnel` au rejet, vous annulez « excellence opérationnelle » du côté gardé,
  sans qu'aucune erreur ne le signale.

### Le test dans les deux sens

À lancer avant d'appliquer un changement, pas après :

```python
import importlib.util, json
sp = importlib.util.spec_from_file_location("sc", "sites-carriere.py")
sc = importlib.util.module_from_spec(sp); sp.loader.exec_module(sc)

s = open("data.js", encoding="utf-8").read(); i = s.index("{", s.index("const DATA"))
d = json.loads(s[i:s.rindex("}") + 1])

jetees  = [o for o in d["offres"] if o.get("statut") in ("jete", "mort")]
retenues = [o for o in d["offres"] if o.get("statut") in ("a-postuler", "postule", "entretien")]

print("jetées encore acceptées :", sum(sc.pertinent(o["poste"], o["lieu"]) for o in jetees))
for o in retenues:                      # AUCUNE ne doit tomber
    if not sc.pertinent(o["poste"], o["lieu"]):
        print("PERDUE :", o["entreprise"], o["poste"])
```

**Mesurez contre ce que l'utilisateur a activement retenu, jamais contre « tout ce qui
n'est pas jeté ».** Une offre non triée n'est pas une offre acceptée : la confondre fait
croire à des faux positifs qui n'existent pas, et masque les vrais.

---

## Ajouter une entreprise

Une ligne dans `sites-carriere.json` :

```json
"Doctolib": { "plateforme": "greenhouse", "id": "doctolib", "tags": ["tech", "sante"] }
```

Les tags sont libres et multiples ; ils servent à filtrer dans l'onglet Entreprises.

Pour trouver la plateforme : `python3 decouvrir-ats.py "Nom"`. Il part de l'adresse du
site carrière, suit les redirections, lit la page, essaie les sous-domaines d'emploi, puis
frappe aux onze points d'entrée connus.

**Vérifiez toujours sur trois offres réelles avant d'inscrire la ligne.** Un identifiant
libre est premier arrivé, premier servi : `decouvrir.py` a déjà proposé « vinci » sur
Ashby, qui est une startup de Palo Alto, et un `/rss` qui rendait douze articles de blog
présentés comme des offres. Un nom qui correspond ne prouve rien.

## Écrire une plateforme qui manque

Le motif est toujours le même : **une fonction qui prend un identifiant et rend une liste
de tuples `(titre, lieu, url, date)`**, puis une entrée dans le dictionnaire `PLATEFORMES`.
Regardez `greenhouse()` pour le cas simple, `workday()` pour un cas difficile.

Trois choses apprises en écrivant les onze existantes :

- **Un `User-Agent` tronqué se fait rendre 403** par certains pare-feux applicatifs, à tous
  les coups. Annoncez un vrai navigateur : la constante `NAVIGATEUR` est là pour ça.
- **« L'URL répond 200 » ne veut pas dire « l'offre est lisible ».** Certaines plateformes
  rendent 200 sur une page de candidature entièrement vide. Ouvrez-en une pour de vrai.
- **Une pagination peut être ignorée en silence.** Un site resservait éternellement la
  première page sans lever d'erreur : 800 offres lues pour 200 distinctes. Comptez les
  identifiants distincts, pas les réponses.

Et une règle de fond : **on n'interroge que des points d'entrée publics, sans
authentification.** Lire le HTML d'une page de résultats casse à chaque refonte de site ;
ce projet s'y refuse, et c'est ce qui lui permet de ne demander aucun entretien.

---

## Toucher à la page

`index.html` est un seul fichier, sans framework et sans build. Le CSS est en haut, le JS
en bas.

**Trois piles, et une offre n'est jamais dans deux à la fois** : le **tri** (ce qui attend
une décision), le **rebut** (jeté ou mort avant d'avoir postulé, visible par le filtre
« caché »), le **suivi** (ce à quoi on a postulé). C'est la présence de `postule_le` qui
range dans le suivi, **pas le statut courant** : un entretien, un refus, une offre morte
après envoi restent des candidatures.

Les animations n'animent qu'`opacity` et `transform`, ne dépassent pas 220 ms, et une
carte n'entre en scène qu'une fois : sans ça, chaque clic rejoue l'animation des centaines
d'autres.

## La forme d'une offre

```json
{
  "id": "sc-a1b2c3",              "entreprise": "Doctolib",
  "poste": "Senior Backend Engineer",
  "lieu": "Paris, France",        "pays": "France",
  "region": "Île-de-France",      "ville": "Paris",
  "contrat": "CDI",               "teletravail": "à vérifier",
  "statut": "a-voir",             "url": "https://…",
  "ajoute": "2026-01-12",         "note": "Site carrière (greenhouse) · trouvée le …",

  "postule_le": "2026-01-14",     "maj": "2026-01-20",
  "rdv": "2026-01-23T14:30",      "rdv_quoi": "Entretien technique",
  "notes": "Ce qui s'est dit au téléphone."
}
```

Statuts : `a-voir` · `a-postuler` · `postule` · `entretien` · `refus` · `jete` · `mort`.
`jete` = écartée avant de postuler ; `refus` = ils ont dit non ; `mort` = l'offre a
disparu, ou abandon après envoi.

Les cinq derniers champs n'existent qu'une fois la candidature envoyée. Le serveur les
écrit sur la route `POST /fiche` ; les statuts passent par `POST /statut`.

---

## Le français partout

Noms de variables, commentaires, messages, noms de fichiers. Ce n'est pas une coquetterie :
le projet se lit comme il s'écrit, et mélanger deux langues rend le code illisible. Les
commentaires disent **pourquoi**, pas quoi — le quoi se lit dans le code.

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

Deux fichiers ne sont **jamais** versionnés : `data.js` et `profil.json`. Ils appartiennent
à l'utilisateur. `data.exemple.js` et `profil.exemple.json` servent de point de départ.
