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
// "disparue_le"  : le jour où l'annonce a cessé d'être en ligne. Posée par la passe
//   de collecte : la plateforme ne la rend plus, et son adresse le confirme. Une offre
//   encore « à voir » passe alors en "mort" ; une offre déjà triée garde son statut.
// "source"       : "manuel" pour une offre ajoutée à la main. Elle n'a pas de
//   plateforme à qui se comparer : la détection de disparition ne la touche jamais.
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
      "rdv": "2026-09-15T14:30",
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
      "nom": "360Learning",
      "url": "https://jobs.lever.co/360learning",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "edtech",
        "remote"
      ]
    },
    {
      "nom": "ABB (CH)",
      "url": "https://abb.wd3.myworkdayjobs.com/External_Career_Page",
      "note": "",
      "tags": [
        "industrie",
        "energie",
        "suisse"
      ]
    },
    {
      "nom": "Accor",
      "url": "https://jobs.smartrecruiters.com/accor",
      "note": "",
      "tags": [
        "cac40",
        "hotellerie"
      ]
    },
    {
      "nom": "AG2R La Mondiale",
      "url": "https://ag2rlamondiale.wd3.myworkdayjobs.com/Candidats",
      "note": "",
      "tags": [
        "banque-assurance"
      ]
    },
    {
      "nom": "Agicap",
      "url": "https://jobs.lever.co/agicap",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    },
    {
      "nom": "Airbus",
      "url": "https://ag.wd3.myworkdayjobs.com/airbus",
      "note": "",
      "tags": [
        "cac40",
        "defense",
        "aeronautique",
        "industrie"
      ]
    },
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
      "url": "https://job-boards.greenhouse.io/algolia",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Ankorstore",
      "url": "https://jobs.ashbyhq.com/ankorstore",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Arabelle Solutions",
      "url": "https://arabellesolutions.wd3.myworkdayjobs.com/Arabelle_Solutions",
      "note": "",
      "tags": [
        "industrie",
        "energie"
      ]
    },
    {
      "nom": "ArianeGroup",
      "url": "https://arianegroup.wd3.myworkdayjobs.com/EXTERNALALL",
      "note": "",
      "tags": [
        "defense",
        "aeronautique",
        "industrie"
      ]
    },
    {
      "nom": "AXA",
      "url": "https://jobs.axa.com/",
      "note": "",
      "tags": [
        "cac40",
        "banque-assurance"
      ]
    },
    {
      "nom": "Back Market",
      "url": "https://jobs.ashbyhq.com/backmarket",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Banque de France",
      "url": "https://bdf.wd103.myworkdayjobs.com/recrutement-banque-de-France",
      "note": "",
      "tags": [
        "public",
        "banque-assurance"
      ]
    },
    {
      "nom": "Believe",
      "url": "https://jobs.smartrecruiters.com/believe",
      "note": "",
      "tags": [
        "tech",
        "medias"
      ]
    },
    {
      "nom": "BlaBlaCar",
      "url": "https://jobs.lever.co/blablacar",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "transport"
      ]
    },
    {
      "nom": "Cardiologs",
      "url": "https://jobs.lever.co/cardiologs",
      "note": "",
      "tags": [
        "tech",
        "sante"
      ]
    },
    {
      "nom": "Chanel",
      "url": "https://cc.wd3.myworkdayjobs.com/ChanelCareers",
      "note": "",
      "tags": [
        "luxe"
      ]
    },
    {
      "nom": "Choose",
      "url": "https://jobs.lever.co/choose",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Contentsquare",
      "url": "https://jobs.lever.co/contentsquare",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Crédit Agricole",
      "url": "https://casa-recrute.talent-soft.com/",
      "note": "",
      "tags": [
        "cac40",
        "banque-assurance"
      ]
    },
    {
      "nom": "Dailymotion",
      "url": "https://jobs.smartrecruiters.com/dailymotion",
      "note": "",
      "tags": [
        "tech",
        "medias"
      ]
    },
    {
      "nom": "Dataiku",
      "url": "https://job-boards.greenhouse.io/dataiku",
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
      "nom": "Dust",
      "url": "https://jobs.ashbyhq.com/dust",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "ia"
      ]
    },
    {
      "nom": "EDF",
      "url": "https://edf-recrute.talent-soft.com/",
      "note": "",
      "tags": [
        "public",
        "energie",
        "industrie"
      ]
    },
    {
      "nom": "Eiffage",
      "url": "https://eiffage.wd3.myworkdayjobs.com/Eiffage_Careers",
      "note": "",
      "tags": [
        "cac40",
        "construction"
      ]
    },
    {
      "nom": "Flink",
      "url": "https://jobs.ashbyhq.com/flink",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Frontify (CH)",
      "url": "https://jobs.ashbyhq.com/frontify",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
      ]
    },
    {
      "nom": "GetYourGuide",
      "url": "https://job-boards.greenhouse.io/getyourguide",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "tourisme"
      ]
    },
    {
      "nom": "Implicity",
      "url": "https://jobs.smartrecruiters.com/implicity",
      "note": "",
      "tags": [
        "tech",
        "sante"
      ]
    },
    {
      "nom": "Ivalua",
      "url": "https://job-boards.greenhouse.io/ivalua",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Julius Baer (CH)",
      "url": "https://juliusbaer.wd3.myworkdayjobs.com/External",
      "note": "",
      "tags": [
        "banque-assurance",
        "suisse"
      ]
    },
    {
      "nom": "Kühne+Nagel",
      "url": "https://jobs.kuehne-nagel.com/",
      "note": "",
      "tags": [
        "transport",
        "logistique",
        "suisse"
      ]
    },
    {
      "nom": "Ledger",
      "url": "https://jobs.ashbyhq.com/ledger",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    },
    {
      "nom": "Lifen",
      "url": "https://jobs.ashbyhq.com/lifen",
      "note": "",
      "tags": [
        "tech",
        "sante"
      ]
    },
    {
      "nom": "Logitech (CH)",
      "url": "https://logitech.wd5.myworkdayjobs.com/Logitech",
      "note": "",
      "tags": [
        "tech",
        "industrie",
        "suisse"
      ]
    },
    {
      "nom": "Lonza (CH)",
      "url": "https://lonza.wd3.myworkdayjobs.com/Lonza_Careers",
      "note": "",
      "tags": [
        "sante",
        "pharma",
        "industrie",
        "suisse"
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
      "nom": "Michelin",
      "url": "https://michelinhr.wd3.myworkdayjobs.com/michelin",
      "note": "",
      "tags": [
        "cac40",
        "industrie"
      ]
    },
    {
      "nom": "Mirakl",
      "url": "https://job-boards.greenhouse.io/mirakl",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce"
      ]
    },
    {
      "nom": "Nabla",
      "url": "https://jobs.ashbyhq.com/nabla",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "sante",
        "ia"
      ]
    },
    {
      "nom": "Nexthink (CH)",
      "url": "https://jobs.smartrecruiters.com/nexthink",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
      ]
    },
    {
      "nom": "Novartis (CH)",
      "url": "https://novartis.wd3.myworkdayjobs.com/Novartis_Careers",
      "note": "",
      "tags": [
        "pharma",
        "sante",
        "suisse"
      ]
    },
    {
      "nom": "Orange",
      "url": "https://orange.wd3.myworkdayjobs.com/Orange_Career",
      "note": "",
      "tags": [
        "cac40",
        "telecom"
      ]
    },
    {
      "nom": "Otis",
      "url": "https://otis.wd504.myworkdayjobs.com/REC_Ext_Gateway",
      "note": "",
      "tags": [
        "industrie"
      ]
    },
    {
      "nom": "Owkin",
      "url": "https://jobs.ashbyhq.com/owkin",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "sante",
        "ia"
      ]
    },
    {
      "nom": "Payfit",
      "url": "https://careers.payfit.com/",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "rh"
      ]
    },
    {
      "nom": "Pennylane",
      "url": "https://jobs.ashbyhq.com/pennylane",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    },
    {
      "nom": "Pernod Ricard",
      "url": "https://pernodricard.wd3.myworkdayjobs.com/pernod-ricard",
      "note": "",
      "tags": [
        "cac40",
        "agroalimentaire"
      ]
    },
    {
      "nom": "Personio",
      "url": "https://personio.recruitee.com/",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "rh"
      ]
    },
    {
      "nom": "PhotoRoom",
      "url": "https://jobs.ashbyhq.com/photoroom",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "ia"
      ]
    },
    {
      "nom": "Pigment",
      "url": "https://jobs.lever.co/pigment",
      "note": "",
      "tags": [
        "tech",
        "scale-up"
      ]
    },
    {
      "nom": "Poolside",
      "url": "https://jobs.ashbyhq.com/poolside",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "ia"
      ]
    },
    {
      "nom": "Proton",
      "url": "https://job-boards.greenhouse.io/proton",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
      ]
    },
    {
      "nom": "Publicis",
      "url": "https://careers.publicisgroupe.com/",
      "note": "",
      "tags": [
        "cac40",
        "medias",
        "publicite"
      ]
    },
    {
      "nom": "Qare",
      "url": "https://qare.recruitee.com/",
      "note": "",
      "tags": [
        "tech",
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
      "nom": "RATP",
      "url": "https://ratp.wd3.myworkdayjobs.com/RATP_Externe",
      "note": "",
      "tags": [
        "public",
        "transport"
      ]
    },
    {
      "nom": "Renault",
      "url": "https://alliancewd.wd3.myworkdayjobs.com/renault-group-careers",
      "note": "",
      "tags": [
        "cac40",
        "automobile",
        "industrie"
      ]
    },
    {
      "nom": "Richemont (CH)",
      "url": "https://richemont.wd3.myworkdayjobs.com/richemont",
      "note": "",
      "tags": [
        "luxe",
        "suisse"
      ]
    },
    {
      "nom": "Roche (CH)",
      "url": "https://roche.wd3.myworkdayjobs.com/roche-ext",
      "note": "",
      "tags": [
        "pharma",
        "sante",
        "suisse"
      ]
    },
    {
      "nom": "Safran",
      "url": "https://careers.safran-group.com/",
      "note": "",
      "tags": [
        "cac40",
        "defense",
        "aeronautique",
        "industrie"
      ]
    },
    {
      "nom": "Saint-Gobain",
      "url": "https://jobs.smartrecruiters.com/saintgobain",
      "note": "",
      "tags": [
        "cac40",
        "industrie",
        "construction"
      ]
    },
    {
      "nom": "Salesforce",
      "url": "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site",
      "note": "",
      "tags": [
        "tech",
        "grand-groupe"
      ]
    },
    {
      "nom": "Sanofi",
      "url": "https://sanofi.wd3.myworkdayjobs.com/SanofiCareers",
      "note": "",
      "tags": [
        "cac40",
        "pharma",
        "sante"
      ]
    },
    {
      "nom": "Scandit (CH)",
      "url": "https://job-boards.greenhouse.io/scandit",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
      ]
    },
    {
      "nom": "Schneider Electric",
      "url": "https://careers.se.com/",
      "note": "",
      "tags": [
        "cac40",
        "industrie",
        "energie"
      ]
    },
    {
      "nom": "Silvr",
      "url": "https://job-boards.greenhouse.io/silvr",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "fintech"
      ]
    },
    {
      "nom": "Smallpdf (CH)",
      "url": "https://jobs.ashbyhq.com/smallpdf",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
      ]
    },
    {
      "nom": "Sodexo",
      "url": "https://jobs.smartrecruiters.com/sodexo",
      "note": "",
      "tags": [
        "cac40",
        "services"
      ]
    },
    {
      "nom": "SonarSource (CH)",
      "url": "https://jobs.lever.co/sonarsource",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "suisse"
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
      "nom": "Stellantis",
      "url": "https://stellantis.wd3.myworkdayjobs.com/External_Career_Site_ID01",
      "note": "",
      "tags": [
        "automobile",
        "industrie"
      ]
    },
    {
      "nom": "Sunday",
      "url": "https://jobs.ashbyhq.com/sunday",
      "note": "",
      "tags": [
        "tech",
        "startup"
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
    },
    {
      "nom": "Swiss Life (CH)",
      "url": "https://swisslife.wd3.myworkdayjobs.com/Swiss_Life_International_Division_Career_Site",
      "note": "",
      "tags": [
        "banque-assurance",
        "suisse"
      ]
    },
    {
      "nom": "Swisscom (CH)",
      "url": "https://swisscom.recruitee.com/",
      "note": "",
      "tags": [
        "telecom",
        "suisse"
      ]
    },
    {
      "nom": "Thales",
      "url": "https://thales.wd3.myworkdayjobs.com/Careers",
      "note": "",
      "tags": [
        "cac40",
        "defense",
        "aeronautique",
        "industrie"
      ]
    },
    {
      "nom": "Trainline",
      "url": "https://jobs.ashbyhq.com/trainline",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "transport"
      ]
    },
    {
      "nom": "Upflow",
      "url": "https://jobs.ashbyhq.com/upflow",
      "note": "",
      "tags": [
        "tech",
        "startup",
        "fintech"
      ]
    },
    {
      "nom": "Valeo",
      "url": "https://valeo.wd3.myworkdayjobs.com/Valeo_Jobs",
      "note": "",
      "tags": [
        "cac40",
        "automobile",
        "industrie"
      ]
    },
    {
      "nom": "Veepee",
      "url": "https://jobs.lever.co/veepee",
      "note": "",
      "tags": [
        "tech",
        "commerce"
      ]
    },
    {
      "nom": "Veolia",
      "url": "https://jobs.veolia.com/",
      "note": "",
      "tags": [
        "cac40",
        "energie",
        "services"
      ]
    },
    {
      "nom": "Verkor",
      "url": "https://jobs.lever.co/verkor",
      "note": "",
      "tags": [
        "industrie",
        "energie",
        "startup"
      ]
    },
    {
      "nom": "Vestiaire Collective",
      "url": "https://jobs.lever.co/vestiairecollective",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "commerce",
        "luxe"
      ]
    },
    {
      "nom": "Vinci",
      "url": "https://jobs.vinci.com/",
      "note": "",
      "tags": [
        "cac40",
        "construction"
      ]
    },
    {
      "nom": "Younited",
      "url": "https://jobs.lever.co/younited",
      "note": "",
      "tags": [
        "tech",
        "scale-up",
        "fintech"
      ]
    }
  ],
  "branchees": [
    "360Learning",
    "ABB (CH)",
    "AG2R La Mondiale",
    "AXA",
    "Accor",
    "Agicap",
    "Airbus",
    "Aircall",
    "Alan",
    "Algolia",
    "Ankorstore",
    "Arabelle Solutions",
    "ArianeGroup",
    "Back Market",
    "Banque de France",
    "Believe",
    "BlaBlaCar",
    "Cardiologs",
    "Chanel",
    "Choose",
    "Contentsquare",
    "Crédit Agricole",
    "Dailymotion",
    "Dataiku",
    "Doctolib",
    "Dust",
    "EDF",
    "Eiffage",
    "Flink",
    "Frontify (CH)",
    "GetYourGuide",
    "Implicity",
    "Ivalua",
    "Julius Baer (CH)",
    "Kühne+Nagel",
    "Ledger",
    "Lifen",
    "Logitech (CH)",
    "Lonza (CH)",
    "Malt",
    "Michelin",
    "Mirakl",
    "Nabla",
    "Nexthink (CH)",
    "Novartis (CH)",
    "Orange",
    "Otis",
    "Owkin",
    "Payfit",
    "Pennylane",
    "Pernod Ricard",
    "Personio",
    "PhotoRoom",
    "Pigment",
    "Poolside",
    "Proton",
    "Publicis",
    "Qare",
    "Qonto",
    "RATP",
    "Renault",
    "Richemont (CH)",
    "Roche (CH)",
    "Safran",
    "Saint-Gobain",
    "Salesforce",
    "Sanofi",
    "Scandit (CH)",
    "Schneider Electric",
    "Silvr",
    "Smallpdf (CH)",
    "Sodexo",
    "SonarSource (CH)",
    "Sorare",
    "Stellantis",
    "Sunday",
    "Swile",
    "Swiss Life (CH)",
    "Swisscom (CH)",
    "Thales",
    "Trainline",
    "Upflow",
    "Valeo",
    "Veepee",
    "Veolia",
    "Verkor",
    "Vestiaire Collective",
    "Vinci",
    "Younited"
  ],
  "ecartees": [],
  "agregateurs": {},
  "sans_api": {}
};
