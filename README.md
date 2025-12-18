# Système d'Analyse Automatisée des Évaluations de Formation

Plateforme web moderne d'analyse automatisée des évaluations de formation avec support multilingue (Français, Arabe, Darija) utilisant le NLP et l'intelligence artificielle.

## Fonctionnalités

- Upload multi-format: Support CSV, Excel, PDF
- Multilingue: Français, Arabe, Darija avec détection automatique
- Analyse NLP automatique:
  - Analyse de sentiment
  - Extraction de thèmes
  - Clustering des évaluations similaires
  - Génération d'insights automatiques
- Dashboard interactif: Visualisations riches et statistiques en temps réel
- Recherche et filtres avancés: Par formation, formateur, langue, sentiment
- Analyse de tendances: Évolution des métriques dans le temps
- Insights automatiques: Recommandations et alertes basées sur l'IA

## Architecture

### Backend
- Framework: FastAPI (Python 3.11+)
- Base de données: PostgreSQL 15
- Cache: Redis 7
- NLP: Hugging Face Inference API
- Modèles:
  - Français: `cmarkea/distilcamembert-base-sentiment`
  - Arabe: `CAMeL-Lab/bert-base-arabic-camelbert-msa-sentiment`
  - Darija: `SI2M-Lab/DarijaBERT`

### Frontend
- Framework: React 18 + Vite
- Styling: TailwindCSS
- State Management: Zustand + React Query
- Charts: Recharts
- UI Icons: Lucide React

## Installation et Démarrage

### Prérequis
- Docker & Docker Compose
- Clé API Hugging Face: https://huggingface.co/settings/tokens

### Configuration

1. Cloner le projet
```bash
cd /home/sebabte/enalyse_auto
```

2. Configurer les variables d'environnement
```bash
cp .env.example .env
```

Éditer `.env` et ajouter votre clé API Hugging Face:
```env
HUGGINGFACE_API_KEY=votre_cle_api_ici
```

3. Lancer avec Docker Compose
```bash
docker-compose up -d
```

Les services seront disponibles sur:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Installation manuelle (sans Docker)

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Utilisation

### 1. Upload de fichiers

Allez sur la page Upload et déposez votre fichier CSV, Excel ou PDF.

Format CSV attendu:
```csv
evaluation_id,formation_id,type_formation,formateur_id,satisfaction,contenu,logistique,applicabilite,commentaire,langue,date
1,F001,Lean Six Sigma,FOR01,5,4,4,3,Formation très utile,FR,2024-01-05
2,F002,SAP,FOR02,3,3,4,4,محتوى جيد,AR,2024-01-06
3,F003,Soft Skills,FOR03,5,5,5,5,Formation mezyana bezzaf,DARIJA,2024-01-07
```

### 2. Dashboard

Visualisez les statistiques globales:
- Nombre total d'évaluations
- Satisfaction moyenne
- Distribution des sentiments
- Langues utilisées
- Thèmes principaux
- Types de formation

### 3. Analyse

Explorez les évaluations détaillées avec:
- Filtres par formation, formateur, langue, sentiment
- Tableau avec résultats NLP pour chaque ligne
- Export des données

### 4. Thèmes

Découvrez les thèmes extraits automatiquement, groupés par langue.

### 5. Clusters

Visualisez les groupes d'évaluations similaires identifiés par clustering.

### 6. Insights

Consultez les découvertes automatiques:
- Tendances
- Alertes (satisfaction faible)
- Recommandations (formateurs excellents)
- Corrélations

## API Endpoints

Documentation interactive disponible sur: http://localhost:8000/docs

Principaux endpoints:
- `POST /api/v1/upload` - Upload de fichiers
- `GET /api/v1/evaluations` - Liste des évaluations
- `GET /api/v1/dashboard/stats` - Statistiques dashboard
- `GET /api/v1/themes` - Thèmes extraits
- `GET /api/v1/clusters` - Clusters
- `GET /api/v1/insights` - Insights
- `GET /api/v1/analytics/trends` - Analyse de tendances
- `POST /api/v1/analytics/generate-insights` - Générer nouveaux insights

## Technologies

**Backend**:
- FastAPI, SQLAlchemy, Pydantic
- Transformers (Hugging Face), Sentence-Transformers
- BERTopic, scikit-learn, HDBSCAN
- Pandas, NumPy, SciPy
- PyPDF2, pdfplumber, openpyxl

**Frontend**:
- React 18, React Router, Vite
- TailwindCSS
- React Query (TanStack Query)
- Recharts, Lucide Icons
- Axios, React Dropzone

**Infrastructure**:
- Docker & Docker Compose
- PostgreSQL, Redis
- Nginx (production)

## Support

Pour toute question ou problème:
- Vérifiez les logs: `docker-compose logs backend frontend`
- Consultez la documentation API: http://localhost:8000/docs
- Vérifiez la connexion à la base de données
- Assurez-vous que votre clé Hugging Face API est valide

## Licence

© 2024 Formation Analytics - Tous droits réservés

## Développement

### Structure du projet
```
enalyse_auto/
├── backend/
│   ├── app/
│   │   ├── api/          # Routes API
│   │   ├── core/         # Configuration
│   │   ├── models/       # Modèles de données
│   │   └── services/     # Services NLP
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/   # Composants React
│   │   ├── pages/        # Pages
│   │   └── services/     # API client
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

### Tests
```bash
# Backend
cd backend
pytest tests/ -v --cov=app

# Frontend
cd frontend
npm test
```
