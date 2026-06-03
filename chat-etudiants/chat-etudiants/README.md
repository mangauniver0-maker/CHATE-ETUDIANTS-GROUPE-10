# Chat Étudiants

Mini app de messagerie pour étudiants d'un groupe, avec code d'accès.
Pur HTML/CSS/JS côté client + FastAPI + MongoDB côté serveur.

## Structure
```
chat-etudiants/
├── backend/
│   ├── server.py        # API FastAPI (~80 lignes)
│   ├── requirements.txt
│   └── .env             # MONGO_URL, DB_NAME
└── frontend/
    ├── index.html       # Page chat (~70 lignes)
    └── admin.html       # Page admin / statistiques
```

## Lancer en local

### 1. MongoDB
Installe MongoDB et lance-le (par défaut sur `mongodb://localhost:27017`).

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend
Sers les fichiers `frontend/` sur un serveur HTTP simple :
```bash
cd frontend
python -m http.server 3000
```

Puis ouvre `http://localhost:3000` dans ton navigateur.

> Si frontend et backend sont sur des domaines/ports différents, modifie
> la ligne `const API = window.location.origin + "/api";` dans `index.html`
> et `admin.html` pour pointer vers `http://localhost:8001/api`.

## Codes d'accès (modifiables dans `server.py`)

| Code | Pseudo |
|---|---|
| ALICE2026 | Alice |
| BOB2026 | Bob |
| CHLOE2026 | Chloé |
| DAVID2026 | David |
| EMMA2026 | Emma |
| FARID2026 | Farid |
| GASPARD2026 | Gaspard |
| HUGO2026 | Hugo |
| INES2026 | Inès |
| JULES2026 | Jules |

## Code admin
- URL : `/admin.html`
- Code : `ADMIN2026`

Affiche : messages totaux, étudiants actifs, activité par heure, classement
par étudiant, 10 derniers messages.

## Ajouter un étudiant
Édite le dict `CODES` dans `backend/server.py` :
```python
CODES = {
    "ALICE2026": "Alice",
    "NOUVEAU2026": "NouvelÉtudiant",
    ...
}
```
Puis redémarre le backend.
