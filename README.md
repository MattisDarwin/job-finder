# job-finder

Une page locale qui va chercher de vraies offres d'emploi sur les sites carrière des
entreprises, les filtre selon **votre** profil, et vous les fait trier d'un clic.

Pas de base de données, pas de compte, pas de dépendance : trois fichiers Python de la
bibliothèque standard, un fichier de données, une page HTML. Tout reste sur votre machine.

> **Ce projet n'est pas fini, et c'est voulu.**
> C'est une charpente conçue pour être modifiée — de préférence par un agent de code qui
> tourne en local, type Claude Code. Le registre d'entreprises est fait pour grossir, le
> filtre pour être réécrit, et une plateforme de recrutement qui manque s'ajoute en une
> fonction. Voir [`AGENTS.md`](AGENTS.md), qui s'adresse justement à cet agent.

---

## Ce que ça fait

**Onglet Offres.** Les annonces collectées, filtrées sur l'intitulé et le lieu. Chaque
carte a cinq boutons : à voir, à postuler, postulé, jeté, mort. Filtres par statut, type
de contrat, pays et ville. Trois densités d'affichage.

**Onglet Suivi.** Ce à quoi vous avez postulé, et depuis combien de jours. Vous y déclarez
la suite — entretien, refus, sans suite — vous notez ce qui s'est dit au téléphone, et
vous fixez la prochaine échéance. Une relance est signalée au bout de dix jours sans
nouvelles.

**Onglet Entreprises.** Les 89 entreprises branchées, filtrables par tag (`cac40`, `tech`,
`defense`, `suisse`, `sante`…). Cliquer sur une entreprise déplie ses offres.

## Comment ça marche

`sites-carriere.py` interroge les **API publiques** des plateformes de recrutement.
Greenhouse, Lever, SmartRecruiters, Ashby, Recruitee, Workday, Phenom, Talentsoft,
Teamtailor, Radancy et Jibe publient toutes un point d'entrée JSON ou RSS **sans
authentification** : les entreprises veulent que leurs offres soient lues, c'est ainsi
qu'elles se diffusent. On ne scrape rien, on utilise la voie prévue, et on plafonne à
25 offres par entreprise et par passe.

`data.js` est la source de vérité unique — lue par la page, écrite par `serveur.py`. Le
navigateur ne peut pas écrire sur le disque : c'est le serveur local qui s'en charge.

## Démarrer

Il faut Python 3. Rien d'autre.

```bash
git clone https://github.com/MattisDarwin/job-finder
cd job-finder

cp profil.exemple.json profil.json      # votre profil de recherche
cp data.exemple.js data.js              # la base, vide

python3 sites-carriere.py               # une passe de collecte (quelques minutes)
open ouvrir.command                     # sert la page et démarre le serveur
```

Sous Linux ou Windows, remplacez la dernière ligne par `python3 serveur.py` puis ouvrez
`http://127.0.0.1:4612/`.

**N'ouvrez jamais `index.html` par double-clic** : la page s'affiche, mais aucun
changement de statut n'est enregistré, faute de serveur.

## Le profil, c'est vous

Tout se joue dans `profil.json`. C'est le seul fichier à écrire pour que l'outil serve
quelqu'un d'autre.

```json
{
  "garde":  ["d[ée]veloppeu?r", "\\bpython\\b", "data\\s+engineer"],
  "ecarte": ["stages?\\b", "\\bvp\\b", "front[\\s-]?end"],
  "lieux":  ["paris", "lyon", "remote"]
}
```

Un intitulé doit contenir **au moins un** motif de `garde`. S'il contient un motif de
`ecarte`, il tombe — le rejet est évalué en premier et gagne toujours. Le lieu doit
contenir un mot de `lieux`.

`profil.exemple.json` est celui de Michel Dupont, développeur backend. Il est commenté et
sert de mode d'emploi par l'exemple.

**Le filtre est volontairement grossier.** Mieux vaut dix offres à écarter qu'une bonne
manquée : c'est vous qui triez ensuite, d'un clic. Et toute modification se teste **dans
les deux sens** — ce qui passe et ce qui tombe. Un filtre qui écarte tout « marche » aussi
bien qu'un filtre qui garde tout.

## Ajouter une entreprise

Le registre est `sites-carriere.json` :

```json
"Doctolib": { "plateforme": "greenhouse", "id": "doctolib", "tags": ["tech", "sante"] }
```

Encore faut-il savoir sur quelle plateforme elle est. C'est le travail de
`decouvrir-ats.py` : il part de l'adresse du site carrière, suit les redirections, lit la
page, essaie les sous-domaines d'emploi, puis frappe aux onze points d'entrée connus.

```bash
python3 decouvrir-ats.py "Nom de l'entreprise"
```

Ce qu'il rend est **une piste, pas une conclusion** : `/rss` existe aussi chez ceux qui
publient un blog. Relisez trois offres réelles avant d'inscrire la ligne.

Deux outils complètent : `decouvrir.py` teste des identifiants contre cinq API — rapide,
mais il confond les homonymes — et `decouvrir-workday.py` cherche les identifiants Workday,
qui ne se devinent pas.

## Les autres scripts

| | |
|---|---|
| `apprendre.py` | cherche ce que vos offres jetées ont en commun et propose des mots à ajouter au filtre. Il propose, il n'applique rien. |
| `logos.py` | récupère une fois les icônes des entreprises et les range en base64. La page reste hors ligne et n'annonce à personne ce que vous regardez. |
| `recolter-workday.py` | trouve des entreprises à partir d'un tenant Workday. |

## Ce qui reste à faire

Des idées, pas des promesses. Repérer les offres dont le lien est mort. Une vue des offres
de plus de trente jours. Brancher les entreprises qui n'ont pas d'API publique — il en
reste beaucoup, et ça demande de lire du HTML, ce que ce projet refuse pour l'instant.

Les contributions sont bienvenues, en particulier de nouvelles plateformes et de nouvelles
entreprises au registre.

## Licence

MIT.
