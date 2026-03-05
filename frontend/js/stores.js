// Alpine.js Global Stores
document.addEventListener('alpine:init', () => {

  // Theme Store
  Alpine.store('theme', {
    dark: false,
    init() {
      const stored = localStorage.getItem('mecrm_theme');
      if (stored) {
        this.dark = stored === 'dark';
      } else {
        this.dark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      }
    },
    toggle() {
      this.dark = !this.dark;
      localStorage.setItem('mecrm_theme', this.dark ? 'dark' : 'light');
    }
  });

  // Toast Notification Store
  Alpine.store('toast', {
    list: [],
    show(msg, type = 'success') {
      const id = Date.now();
      this.list.push({ id, msg, type });
      setTimeout(() => this.remove(id), 3500);
    },
    remove(id) {
      this.list = this.list.filter(t => t.id !== id);
    },
    success(msg) { this.show(msg, 'success'); },
    error(msg) { this.show(msg, 'error'); },
    info(msg) { this.show(msg, 'info'); }
  });

  // Auth Store
  Alpine.store('auth', {
    user: null,
    loading: true,

    async init() {
      if (!AuthManager.isAuthenticated()) {
        this.loading = false;
        return;
      }
      try {
        this.user = await API.getMe();
        this.loading = false;
      } catch (error) {
        AuthManager.clearToken();
        this.user = null;
        this.loading = false;
      }
    },

    async login(email, password) {
      try {
        await API.login(email, password);
        this.user = await API.getMe();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    },

    async register(name, email, password) {
      try {
        await API.register(name, email, password);
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

  // Data Store
  Alpine.store('data', {
    contacts: [],
    deals: [],
    dashboard: null,

    emit(event, data) {
      window.dispatchEvent(new CustomEvent(event, { detail: data }));
    },

    async refreshContacts() {
      try {
        this.contacts = await API.getContacts();
        this.emit('contacts-updated', this.contacts);
      } catch (error) {
        console.error('Failed to refresh contacts:', error);
      }
    },

    async refreshDeals() {
      try {
        this.deals = await API.getDeals();
        this.emit('deals-updated', this.deals);
      } catch (error) {
        console.error('Failed to refresh deals:', error);
      }
    }
  });

});
