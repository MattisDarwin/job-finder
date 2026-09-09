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
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple02",
      "entreprise": "Doctolib",
      "poste": "Staff Engineer - Platform",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://job-boards.greenhouse.io/doctolib",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple03",
      "entreprise": "Qonto",
      "poste": "Data Engineer - Platform",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-postuler",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/qonto",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple04",
      "entreprise": "Qonto",
      "poste": "Backend Engineer - Payments",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://jobs.lever.co/qonto",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple05",
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
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre.",
      "postule_le": "2026-08-28",
      "maj": "2026-09-03"
    },
    {
      "id": "sc-exemple06",
      "entreprise": "Algolia",
      "poste": "Senior Software Engineer - Search",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/algolia",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple07",
      "entreprise": "Alan",
      "poste": "Backend Engineer (Go)",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "entretien",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.ashbyhq.com/alan",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre.",
      "postule_le": "2026-08-19",
      "maj": "2026-08-30",
      "rdv": "2026-09-13T14:30",
      "rdv_quoi": "Entretien technique",
      "notes": "Premier échange le 12 : équipe de six, stack Go et Kubernetes.\nÀ préparer : relire leur article sur la migration monolithe -> services.\nIls demandent un exercice de code en amont."
    },
    {
      "id": "sc-exemple08",
      "entreprise": "Pennylane",
      "poste": "Développeur Backend Python",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://jobs.lever.co/pennylane",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple09",
      "entreprise": "Mirakl",
      "poste": "Cloud Infrastructure Engineer",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/mirakl",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple10",
      "entreprise": "Aircall",
      "poste": "Senior Data Engineer",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "refus",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/aircall",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre.",
      "postule_le": "2026-08-06",
      "maj": "2026-08-23"
    },
    {
      "id": "sc-exemple11",
      "entreprise": "Swile",
      "poste": "DevOps Engineer",
      "lieu": "Lyon, France",
      "pays": "France",
      "region": "Auvergne-Rhône-Alpes",
      "ville": "Lyon",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://jobs.lever.co/swile",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple12",
      "entreprise": "Back Market",
      "poste": "Platform Engineer - Kubernetes",
      "lieu": "Bordeaux, France",
      "pays": "France",
      "region": "Nouvelle-Aquitaine",
      "ville": "Bordeaux",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/backmarket",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple13",
      "entreprise": "Dataiku",
      "poste": "Backend Engineer - API",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://boards.greenhouse.io/dataiku",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple14",
      "entreprise": "Malt",
      "poste": "Développeur Go - Marketplace",
      "lieu": "Remote",
      "pays": "Remote",
      "region": "",
      "ville": "",
      "teletravail": "oui",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "",
      "url": "https://jobs.lever.co/malt",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    },
    {
      "id": "sc-exemple15",
      "entreprise": "Sorare",
      "poste": "Senior Backend Engineer",
      "lieu": "Paris, France",
      "pays": "France",
      "region": "Île-de-France",
      "ville": "Paris",
      "teletravail": "à vérifier",
      "piste": "1",
      "statut": "a-voir",
      "priorite": 15,
      "contrat": "CDI",
      "url": "https://jobs.ashbyhq.com/sorare",
      "ajoute": "2026-09-09",
      "note": "Offre d'exemple — remplacez ce fichier par le vôtre."
    }
  ],
  "entreprises": [
    {
      "nom": "Aircall",
      "url": "https://jobs.lever.co/aircall",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Alan",
      "url": "https://jobs.ashbyhq.com/alan",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "sante",
        "assurtech"
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
    },
    {
      "nom": "Back Market",
      "url": "https://jobs.lever.co/backmarket",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Dataiku",
      "url": "https://boards.greenhouse.io/dataiku",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "ia"
      ]
    },
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
      "nom": "Malt",
      "url": "https://jobs.lever.co/malt",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Mirakl",
      "url": "https://jobs.lever.co/mirakl",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Pennylane",
      "url": "https://jobs.lever.co/pennylane",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
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
      "nom": "Sorare",
      "url": "https://jobs.ashbyhq.com/sorare",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    },
    {
      "nom": "Swile",
      "url": "https://jobs.lever.co/swile",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "rh"
      ]
    }
  ],
  "branchees": [
    "Aircall",
    "Alan",
    "Algolia",
    "Back Market",
    "Dataiku",
    "Doctolib",
    "Malt",
    "Mirakl",
    "Pennylane",
    "Qonto",
    "Sorare",
    "Swile"
  ],
  "ecartees": [],
  "agregateurs": {},
  "sans_api": {}
};
