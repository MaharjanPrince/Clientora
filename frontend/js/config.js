// API Configuration
const API_BASE_URL = 'http://127.0.0.1:8000';

// Auth Helper Functions
const AuthManager = {
  // Get stored token
  getToken() {
    return localStorage.getItem('token');
  },
  
  // Store token after login
  setToken(token) {
    localStorage.setItem('token', token);
  },
  
  // Remove token on logout
  clearToken() {
    localStorage.removeItem('token');
  },
  
  // Check if user is authenticated
  isAuthenticated() {
    return !!this.getToken();
  },
  
  // Redirect to login if not authenticated
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
  
  // Add Authorization header if token exists
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
  
  // If 401, token is invalid - logout
  if (response.status === 401) {
    AuthManager.clearToken();
    window.location.href = 'index.html';
    throw new Error('Session expired. Please login again.');
  }
  
  // If not ok, throw error with message
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
}

// Convenience methods
const API = {
  // Auth
  async login(email, password) {
    // FastAPI OAuth2 expects form data, not JSON
    const formData = new URLSearchParams();
    formData.append('username', email); // OAuth2 calls it 'username' but we send email
    formData.append('password', password);
    
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData
    });
    
    if (!response.ok) {
      throw new Error('Invalid credentials');
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
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    return response.json();
  },
  
  async getMe() {
    return apiFetch('/auth/me');
  },
  
  // Dashboard
  async getDashboard() {
    return apiFetch('/dashboard');
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
    return apiFetch(`/contacts/${id}`, {
      method: 'DELETE'
    });
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
  async getDeals() {
    return apiFetch('/deals');
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
    return apiFetch(`/deals/${id}`, {
      method: 'DELETE'
    });
  }
};