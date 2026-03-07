// API Configuration
const API_BASE_URL = 'https://clientora-backend.onrender.com';

// Auth Helper Functions
const AuthManager = {
  getToken() {
    return localStorage.getItem('mecrm_token');
  },
  setToken(token) {
    localStorage.setItem('mecrm_token', token);
  },
  clearToken() {
    localStorage.removeItem('mecrm_token');
    localStorage.removeItem('mecrm_user');
  },
  isAuthenticated() {
    return !!this.getToken();
  },
  requireAuth() {
    if (!this.isAuthenticated()) {
      window.location.href = 'index.html';
    }
  }
};

// Authenticated Fetch Wrapper
async function apiFetch(endpoint, options = {}) {
  const token = AuthManager.getToken();

  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    }
  };

  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

  if (response.status === 401) {
    AuthManager.clearToken();
    window.location.href = 'index.html';
    throw new Error('Session expired. Please login again.');
  }

  if (response.status === 204) {
    return null;
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    // FastAPI 422 validation errors return detail as an array
    if (Array.isArray(error.detail)) {
      const messages = error.detail.map(e => e.msg).join(', ');
      throw new Error(messages || 'Validation failed');
    }
    throw new Error(error.detail || 'Request failed');
  }

  return response.json();
}

// Convenience methods
const API = {
  // Auth
  async login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: formData
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || 'Invalid credentials');
    }

    const data = await response.json();
    AuthManager.setToken(data.access_token);
    return data;
  },

  async register(name, email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password })
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      // FastAPI 422 returns { detail: [ {loc, msg, type} ] }
      if (Array.isArray(error.detail)) {
        const messages = error.detail.map(e => e.msg).join(', ');
        throw new Error(messages || 'Validation failed');
      }
      throw new Error(error.detail || 'Registration failed');
    }

    return response.json();
  },

  async getMe() {
    return apiFetch('/auth/me');
  },

  // Dashboard
  async getDashboard() {
    return apiFetch('/dashboard/');
  },

  // Contacts
  async getContacts() {
    return apiFetch('/contacts');
  },

  async getContact(id) {
    return apiFetch(`/contacts/${id}`);
  },

  async createContact(data) {
    return apiFetch('/contacts', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateContact(id, data) {
    return apiFetch(`/contacts/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteContact(id) {
    return apiFetch(`/contacts/${id}`, { method: 'DELETE' });
  },

  // Notes
  async getNotes(contactId) {
    return apiFetch(`/contacts/${contactId}/notes`);
  },

  async createNote(contactId, data) {
    return apiFetch(`/contacts/${contactId}/notes`, {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // AI Context
  async getContactContext(contactId) {
    return apiFetch(`/contacts/${contactId}/context`);
  },

  // Deals
  async getDeals(stage = null) {
    const qs = stage ? `?stage=${stage}` : '';
    return apiFetch(`/deals${qs}`);
  },

  async createDeal(data) {
    return apiFetch('/deals', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  async updateDeal(id, data) {
    return apiFetch(`/deals/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data)
    });
  },

  async deleteDeal(id) {
    return apiFetch(`/deals/${id}`, { method: 'DELETE' });
  }
};