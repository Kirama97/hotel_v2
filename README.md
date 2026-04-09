#  Hotel App v2 — Django REST + React + Cloudinary

Backend Django REST Framework avec :
- Authentification JWT (SimpleJWT)
- CRUD hôtels complet
- Images uploadées sur **Cloudinary**
- Base de données **PostgreSQL**
- Tout utilisateur connecté voit **tous les hôtels**
- CORS ouvert pour tous les ports localhost (Vite)

---

## 📁 Structure

```
hotel_v2/
├── hotel_backend/
│   ├── __init__.py
│   ├── settings.py        ← Config DB, JWT, Cloudinary, CORS
│   ├── urls.py
│   └── wsgi.py
│
├── authentication/
│   ├── models.py          ← User personnalisé (email = identifiant)
│   ├── serializers.py     ← Register sans confirm password
│   ├── views.py           ← Register, Login, Logout, Users, Reset, Change
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── hotels/
│   ├── models.py          ← Hotel avec CloudinaryField
│   ├── serializers.py     ← URLs Cloudinary optimisées
│   ├── views.py           ← CRUD complet + toggle + stats
│   ├── urls.py
│   ├── admin.py
│   └── apps.py
│
├── frontend/
│   └── services/
│       └── api.js         ← Service Axios (à copier dans votre React)
│
├── manage.py
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Prérequis
- Python 3.10+
- PostgreSQL installé et démarré
- Compte Cloudinary (gratuit sur https://cloudinary.com)

### 2. Environnement virtuel et dépendances

```bash
python -m venv env
        # Windows : env\Scripts\activate
pip install -r requirements.txt
```

### 3. Base de données PostgreSQL

```sql
-- Dans psql ou pgAdmin :
CREATE DATABASE hotel_db;
```

### 4. Configurer settings.py

**Base de données :**
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'hotel_db',
        'USER': 'postgres',      
        'PASSWORD': 'votre_mdp', 
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

**Cloudinary** (depuis https://dashboard.cloudinary.com) :
```python
cloudinary.config(
    cloud_name = 'root',
    api_key    = '638491166864998',
    api_secret = 'wFfwlJjgo6OOYIL3bccvWIbmSQc',
    secure     = True,
)
```

### 5. Migrations et lancement

```bash
python manage.py makemigrations authentication
python manage.py makemigrations hotels
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Le backend tourne sur : **http://127.0.0.1:8000**
Admin Django : **http://127.0.0.1:8000/admin/**

---

## 🔌 Endpoints API

### Authentification `/api/auth/`

| Méthode | URL | Auth | Description |
|---------|-----|:----:|-------------|
| POST | `/api/auth/register/` | ✗ | Inscription (username + email + password) |
| POST | `/api/auth/login/` | ✗ | Connexion → access + refresh tokens |
| POST | `/api/auth/token/refresh/` | ✗ | Rafraîchir le access token |
| POST | `/api/auth/logout/` | ✓ | Déconnexion |
| GET | `/api/auth/me/` | ✓ | Profil utilisateur connecté |
| PUT | `/api/auth/me/` | ✓ | Modifier le profil |
| GET | `/api/auth/users/` | ✓ | Liste tous les utilisateurs inscrits |
| POST | `/api/auth/password/reset/` | ✗ | Demander un token de reset |
| POST | `/api/auth/password/confirm/` | ✗ | Confirmer le reset |
| PUT | `/api/auth/password/change/` | ✓ | Changer le mot de passe |

### Hôtels `/api/hotels/`

| Méthode | URL | Auth | Description |
|---------|-----|:----:|-------------|
| GET | `/api/hotels/` | ✓ | Tous les hôtels (tous utilisateurs) |
| POST | `/api/hotels/` | ✓ | Créer un hôtel |
| GET | `/api/hotels/{id}/` | ✓ | Détail d'un hôtel |
| PUT | `/api/hotels/{id}/` | ✓ | Modifier (créateur uniquement) |
| PATCH | `/api/hotels/{id}/` | ✓ | Modifier partiellement (créateur) |
| DELETE | `/api/hotels/{id}/` | ✓ | Supprimer (créateur uniquement) |
| PATCH | `/api/hotels/{id}/toggle-disponibilite/` | ✓ | Activer/désactiver (créateur) |
| GET | `/api/hotels/statistiques/` | ✓ | Stats globales |

#### Filtres disponibles pour `GET /api/hotels/`

```
?search=dakar           → recherche texte (nom, ville, pays, description)
?etoiles=4              → filtrer par étoiles (1-5)
?disponible=true        → filtrer par disponibilité
?ville=Dakar            → filtrer par ville
?ordering=prix_par_nuit → trier par prix croissant
?ordering=-etoiles      → trier par étoiles décroissant
?page=2                 → pagination (10 par page)
```

---

##  Exemples de requêtes

### Inscription
```json
POST /api/auth/register/
{
    "username": "kira",
    "email": "kira@example.com",
    "password": "Passe123!"
}
→ 201 : { "user": {...}, "tokens": { "access": "...", "refresh": "..." } }
```

### Connexion
```json
POST /api/auth/login/
{
    "email": "kira@example.com",
    "password": "Passe123!"
}
→ 200 : { "access": "eyJ...", "refresh": "eyJ..." }
```

### Créer un hôtel (avec image)
```
POST /api/hotels/
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

nom=Hôtel Terrou-Bi
adresse=Corniche Ouest
ville=Dakar
etoiles=5
prix_par_nuit=150000
nombre_chambres=120
image=<fichier image>
```

### Reset password — Étape 1
```json
POST /api/auth/password/reset/
{ "email": "john@example.com" }
→ { "token": "550e8400-...", "expires_in": "24 heures" }
```

### Reset password — Étape 2
```json
POST /api/auth/password/confirm/
{
    "token": "550e8400-e29b-41d4-a716-446655440000",
    "new_password": "NouveauMdp456!"
}
→ { "message": "Mot de passe réinitialisé avec succès." }
```

---

##  Cloudinary — upload d'image depuis React

```javascript
import { createHotel } from './services/api';

const handleSubmit = async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append('nom', nom);
  formData.append('adresse', adresse);
  formData.append('ville', ville);
  formData.append('etoiles', etoiles);
  formData.append('prix_par_nuit', prix);
  formData.append('nombre_chambres', chambres);

  // fichierImage = e.target.files[0] depuis un <input type="file">
  if (fichierImage) {
    formData.append('image', fichierImage);
  }

  try {
    const { data } = await createHotel(formData);
    console.log('Hôtel créé :', data);
    console.log('Image URL :', data.image_url); // URL Cloudinary optimisée
  } catch (error) {
    console.error(error.response?.data);
  }
};
```

---

##  Utilisation du service api.js dans React

```javascript
// Copier frontend/services/api.js dans votre projet React

import {
  login, logout, register,
  getHotels, createHotel, updateHotel, deleteHotel,
  getUsers
} from './services/api';

// Connexion
const handleLogin = async () => {
  await login({ email, password });
  navigate('/dashboard'); // ← votre route
};

// Inscription
const handleRegister = async () => {
  const { data } = await register({ username, email, password });
  localStorage.setItem('access_token', data.tokens.access);
  localStorage.setItem('refresh_token', data.tokens.refresh);
  navigate('/dashboard');
};

// Liste de tous les hôtels
const { data } = await getHotels({ etoiles: 4, disponible: 'true' });
const hotels = data.results; // tableau paginé

// Liste des utilisateurs inscrits
const { data: users } = await getUsers();

// Déconnexion
await logout();
navigate('/connexion');
```

---

##  Règles métier

| Action | Qui peut faire ? |
|--------|-----------------|
| Voir tous les hôtels | Tout utilisateur connecté |
| Créer un hôtel | Tout utilisateur connecté |
| Modifier un hôtel | Créateur uniquement (403 sinon) |
| Supprimer un hôtel | Créateur uniquement (403 sinon) |
| Toggle disponibilité | Créateur uniquement (403 sinon) |
| Voir les utilisateurs | Tout utilisateur connecté |

---

##  Commandes utiles

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver

# Shell Django
python manage.py shell
```
