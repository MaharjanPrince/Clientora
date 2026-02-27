// Alpine.js Global Stores
document.addEventListener('alpine:init', () => {
  
  // Theme Store (Dark Mode)
  Alpine.store('theme', {
    dark: false,
    
    init() {
      // Check localStorage or system preference
      const stored = localStorage.getItem('theme');
      if (stored) {
        this.dark = stored === 'dark';
      } else {
        // Check system preference
        this.dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      }
    },
    
    toggle() {
      this.dark = !this.dark;
      localStorage.setItem('theme', this.dark ? 'dark' : 'light');
    }
  });
  
  // Toast Notification Store
  Alpine.store('toast', {
    list: [],
    
    show(msg, type = 'success') {
      const id = Date.now();
      this.list.push({ id, msg, type });
      
      // Auto-remove after 3.5 seconds
      setTimeout(() => this.remove(id), 3500);
    },
    
    remove(id) {
      this.list = this.list.filter(t => t.id !== id);
    },
    
    success(msg) {
      this.show(msg, 'success');
    },
    
    error(msg) {
      this.show(msg, 'error');
    },
    
    info(msg) {
      this.show(msg, 'info');
    }
  });
  
  // Modal Store
  Alpine.store('modal', {
    open: false,
    view: null,
    data: null,
    
    show(view, data = null) {
      this.open = true;
      this.view = view;
      this.data = data;
    },
    
    close() {
      this.open = false;
      this.view = null;
      this.data = null;
    }
  });
  
  // Auth Store (REAL implementation)
  Alpine.store('auth', {
    user: null,
    loading: true,
    
    async init() {
      // Check if token exists
      if (!AuthManager.isAuthenticated()) {
        this.loading = false;
        return;
      }
      
      // Try to fetch current user
      try {
        this.user = await API.getMe();
        this.loading = false;
      } catch (error) {
        console.error('Failed to fetch user:', error);
        // Token is invalid, clear it
        AuthManager.clearToken();
        this.user = null;
        this.loading = false;
      }
    },
    
    async login(email, password) {
      try {
        await API.login(email, password);
        // Fetch user data
        this.user = await API.getMe();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    },
    
    async register(name, email, password) {
      try {
        await API.register(name, email, password);
        // After registration, login automatically
        await API.login(email, password);
        this.user = await API.getMe();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    },
    
    logout() {
      AuthManager.clearToken();
      this.user = null;
      window.location.href = 'index.html';
    },
    
    get isAuthenticated() {
      return !!this.user;
    }
  });
  
  // Data Store (for caching and events)
  Alpine.store('data', {
    contacts: [],
    deals: [],
    dashboard: null,
    
    // Event emitter for component updates
    emit(event, data) {
      window.dispatchEvent(new CustomEvent(event, { detail: data }));
    },
    
    // Refresh contacts
    async refreshContacts() {
      try {
        this.contacts = await API.getContacts();
        this.emit('contacts-updated', this.contacts);
      } catch (error) {
        console.error('Failed to refresh contacts:', error);
      }
    },
    
    // Refresh deals
    async refreshDeals() {
      try {
        this.deals = await API.getDeals();
        this.emit('deals-updated', this.deals);
      } catch (error) {
        console.error('Failed to refresh deals:', error);
      }
    },
    
    // Refresh dashboard
    async refreshDashboard() {
      try {
        this.dashboard = await API.getDashboard();
        this.emit('dashboard-updated', this.dashboard);
      } catch (error) {
        console.error('Failed to refresh dashboard:', error);
      }
    }
  });
  
});