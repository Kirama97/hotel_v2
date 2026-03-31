/**
 * services/api.js
 *
 * Service Axios centralisé — Hotel App v2
 *
 * Fonctionnalités :
 * - Injection automatique du JWT dans chaque requête
 * - Rafraîchissement automatique du token si expiré (401)
 * - Redirection vers /connexion si le refresh token est aussi expiré
 * - Toutes les fonctions auth + hotels en un seul fichier
 *
 * Installation :
 *   npm install axios
 *
 * Usage :
 *   import { login, getHotels, createHotel } from './services/api';
 */

import axios from 'axios';

// ─────────────────────────────────────────────────────────────────────────────
// CONFIGURATION DE BASE
// ─────────────────────────────────────────────────────────────────────────────

const API_URL = 'http://127.0.0.1:8000/api';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─────────────────────────────────────────────────────────────────────────────
// INTERCEPTEUR REQUEST — injecte le JWT automatiquement
// ─────────────────────────────────────────────────────────────────────────────

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─────────────────────────────────────────────────────────────────────────────
// INTERCEPTEUR RESPONSE — rafraîchit le token si expiré (401)
// ─────────────────────────────────────────────────────────────────────────────

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const { data } = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        // Sauvegarder le nouveau access token
        localStorage.setItem('access_token', data.access);

        // Relancer la requête originale avec le nouveau token
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return api(originalRequest);

      } catch {
        // Refresh token expiré → déconnecter
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        // ✅ Correspond à votre route React /connexion
        window.location.href = '/connexion';
      }
    }

    return Promise.reject(error);
  }
);

// ─────────────────────────────────────────────────────────────────────────────
// AUTHENTIFICATION
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Inscription — username + email + password (pas de confirm password)
 * @param {{ username: string, email: string, password: string }} data
 * @returns {{ user, tokens: { access, refresh }, message }}
 *
 * Exemple :
 *   const { data } = await register({ username: 'john', email: 'john@ex.com', password: 'Mdp123!' });
 *   localStorage.setItem('access_token', data.tokens.access);
 *   localStorage.setItem('refresh_token', data.tokens.refresh);
 */
export const register = (data) => api.post('/auth/register/', data);

/**
 * Connexion — retourne access + refresh tokens
 * Les tokens sont sauvegardés automatiquement dans localStorage.
 * @param {{ email: string, password: string }} data
 *
 * Exemple :
 *   await login({ email: 'john@ex.com', password: 'Mdp123!' });
 *   navigate('/dashboard');
 */
export const login = async (data) => {
  const response = await api.post('/auth/login/', data);
  localStorage.setItem('access_token', response.data.access);
  localStorage.setItem('refresh_token', response.data.refresh);
  return response;
};

/**
 * Déconnexion — blackliste le refresh token côté serveur
 * localStorage vidé automatiquement.
 *
 * Exemple :
 *   await logout();
 *   navigate('/connexion');
 */
export const logout = async () => {
  const refresh = localStorage.getItem('refresh_token');
  try {
    await api.post('/auth/logout/', { refresh });
  } finally {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }
};

/**
 * Récupérer le profil de l'utilisateur connecté
 * @returns {{ id, username, email, first_name, last_name, date_joined }}
 */
export const getProfile = () => api.get('/auth/me/');

/**
 * Modifier le profil (username, first_name, last_name)
 * @param {{ username?, first_name?, last_name? }} data
 */
export const updateProfile = (data) => api.put('/auth/me/', data);

/**
 * Liste de tous les utilisateurs inscrits avec leur nombre d'hôtels
 * @returns {Array<{ id, username, email, date_joined, total_hotels }>}
 *
 * Exemple d'utilisation React :
 *   const { data } = await getUsers();
 *   // data = [{ id:1, username:'john', email:'...', total_hotels: 3 }, ...]
 */
export const getUsers = () => api.get('/auth/users/');

// ─── Reset Password (sans email, token dans la réponse) ───────────────────────

/**
 * Étape 1 : Demander un token de reset
 * @param {string} email
 * @returns {{ message, token, expires_in }}
 *
 * Exemple :
 *   const { data } = await requestPasswordReset('john@ex.com');
 *   console.log(data.token); // UUID à utiliser dans confirmPasswordReset
 */
export const requestPasswordReset = (email) =>
  api.post('/auth/password/reset/', { email });

/**
 * Étape 2 : Confirmer le reset avec le token reçu
 * @param {{ token: string, new_password: string }} data
 *
 * Exemple :
 *   await confirmPasswordReset({ token: uuid, new_password: 'NouveauMdp123!' });
 *   navigate('/connexion');
 */
export const confirmPasswordReset = (data) =>
  api.post('/auth/password/confirm/', data);

/**
 * Changer le mot de passe (utilisateur déjà connecté)
 * @param {{ old_password: string, new_password: string }} data
 */
export const changePassword = (data) =>
  api.put('/auth/password/change/', data);

// ─────────────────────────────────────────────────────────────────────────────
// HOTELS — CRUD COMPLET
// ─────────────────────────────────────────────────────────────────────────────

/**
 * Liste de tous les hôtels (tous les utilisateurs)
 * @param {Object} params - Filtres optionnels
 * @param {string}  [params.search]      Recherche texte dans nom/ville/pays
 * @param {number}  [params.etoiles]     1 à 5
 * @param {string}  [params.disponible]  'true' ou 'false'
 * @param {string}  [params.ville]       Filtrer par ville
 * @param {string}  [params.ordering]    Ex: 'prix_par_nuit' ou '-etoiles'
 * @param {number}  [params.page]        Numéro de page (pagination)
 *
 * Exemple :
 *   const { data } = await getHotels({ etoiles: 4, disponible: 'true' });
 *   // data.results = tableau des hôtels, data.count = total
 */
export const getHotels = (params = {}) => api.get('/hotels/', { params });

/**
 * Détail d'un hôtel
 * @param {number} id
 */
export const getHotel = (id) => api.get(`/hotels/${id}/`);

/**
 * Créer un hôtel
 * Supporte FormData pour l'upload d'image vers Cloudinary.
 * @param {FormData | Object} data
 *
 * Exemple avec image :
 *   const formData = new FormData();
 *   formData.append('nom', 'Hôtel Terrou-Bi');
 *   formData.append('ville', 'Dakar');
 *   formData.append('etoiles', 5);
 *   formData.append('prix_par_nuit', '150000');
 *   formData.append('adresse', 'Corniche Ouest');
 *   formData.append('nombre_chambres', 50);
 *   formData.append('image', fichierImage); // File object depuis <input type="file">
 *   await createHotel(formData);
 *
 * Exemple sans image :
 *   await createHotel({ nom: 'Hôtel', ville: 'Dakar', etoiles: 3, prix_par_nuit: 50000, adresse: '...', nombre_chambres: 10 });
 */
export const createHotel = (data) => {
  const isFormData = data instanceof FormData;
  return api.post('/hotels/', data, {
    headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {},
  });
};

/**
 * Modifier un hôtel entièrement (PUT)
 * Seul le créateur peut modifier.
 * @param {number} id
 * @param {FormData | Object} data
 */
export const updateHotel = (id, data) => {
  const isFormData = data instanceof FormData;
  return api.put(`/hotels/${id}/`, data, {
    headers: isFormData ? { 'Content-Type': 'multipart/form-data' } : {},
  });
};

/**
 * Modifier un hôtel partiellement (PATCH)
 * Seul le créateur peut modifier.
 * @param {number} id
 * @param {Object} data - Seulement les champs à changer
 *
 * Exemple :
 *   await patchHotel(1, { prix_par_nuit: '85000', est_disponible: false });
 */
export const patchHotel = (id, data) => api.patch(`/hotels/${id}/`, data);

/**
 * Supprimer un hôtel
 * Seul le créateur peut supprimer.
 * @param {number} id
 */
export const deleteHotel = (id) => api.delete(`/hotels/${id}/`);

/**
 * Basculer la disponibilité d'un hôtel (activer / désactiver)
 * Seul le créateur peut effectuer cette action.
 * @param {number} id
 */
export const toggleDisponibilite = (id) =>
  api.patch(`/hotels/${id}/toggle-disponibilite/`);

/**
 * Statistiques globales sur tous les hôtels
 * @returns {{
 *   total_hotels, hotels_disponibles,
 *   prix_moyen, prix_min, prix_max,
 *   etoiles_moyenne, total_chambres,
 *   par_ville: Array<{ ville, count }>
 * }}
 */
export const getStatistiques = () => api.get('/hotels/statistiques/');

export default api;
