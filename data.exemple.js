// Source de vérité unique : lue par index.html, écrite par serveur.py.
// CE FICHIER EST UN EXEMPLE. Copiez-le en data.js et lancez sites-carriere.py :
//     cp data.exemple.js data.js && python3 sites-carriere.py
//
// Clés : offres · entreprises · branchees · ecartees · agregateurs · sans_api
// Statuts : "a-voir" · "a-postuler" · "postule" · "entretien" · "refus" · "jete" · "mort"
//   "jete" = écartée avant de postuler · "refus" = ils ont dit non
//   "mort" = l'offre a disparu, ou abandon après avoir postulé
// "postule_le" : la date du premier envoi. Gravée une fois, jamais réécrite — c'est elle
//   qui range l'offre dans l'onglet Suivi et qui compte les jours.
// "contrat" : "VIE" · "CDI" · "CDD" · "" quand l'intitulé n'en dit rien.
// "notes" · "rdv" · "rdv_quoi" : le compte rendu d'un échange et la prochaine échéance.
const DATA = {
  "offres": [
    {
      "id": "sc-exemple01",
      "entreprise": "Doctolib",
      "poste": "Senior Backend Engineer (Python)",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://job-boards.greenhouse.io/doctolib",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple · trouvée le 2026-09-09"
    },
    {
      "id": "sc-exemple02",
      "entreprise": "Qonto",
      "poste": "Data Engineer - Platform",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "oui",
      "piste": "1",
      "statut": "a-postuler",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/qonto",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple · celle-ci est marquée « à postuler »"
    },
    {
      "id": "sc-exemple03",
      "entreprise": "Algolia",
      "poste": "Site Reliability Engineer",
      "lieu": "Remote",
      "pays": "Remote",
      "region": "",
      "ville": "",
      "teletravail": "oui",
      "piste": "1",
      "statut": "postule",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://jobs.lever.co/algolia",
      "ajoute": "2026-09-09",
      "postule_le": "2026-09-09",
      "maj": "2026-09-09",
      "note": "Offre d'exemple · postulée, elle apparaît donc dans l'onglet Suivi",
      "rdv_quoi": "Entretien technique",
      "notes": "Exemple de notes : ce qui s'est dit, quoi préparer."
    }
  ],
  "entreprises": [
    {
      "nom": "Doctolib",
      "url": "https://job-boards.greenhouse.io/doctolib",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "sante"
      ]
    },
    {
      "nom": "Qonto",
      "url": "https://jobs.lever.co/qonto",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    },
    {
      "nom": "Algolia",
      "url": "https://jobs.lever.co/algolia",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    }
  ],
  "branchees": [
    "Algolia",
    "Doctolib",
    "Qonto"
  ],
  "ecartees": [],
  "agregateurs": {},
  "sans_api": {}
};
