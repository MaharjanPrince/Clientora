// Dashboard Stats Component
document.addEventListener('alpine:init', () => {
  
  Alpine.data('dashboardStats', () => ({
    dashboard: null,
    loading: true,
    error: null,
    
    async init() {
      await this.fetchDashboard();
      
      // Listen for refresh events
      window.addEventListener('dashboard-updated', (e) => {
        this.dashboard = e.detail || Alpine.store('data').dashboard;
      });
    },
    
    async fetchDashboard() {
      this.loading = true;
      this.error = null;
      
      try {
        this.dashboard = await API.getDashboard();
        Alpine.store('data').dashboard = this.dashboard;
      } catch (error) {
        console.error('Failed to load dashboard:', error);
        this.error = error.message;
        Alpine.store('toast').error('Failed to load dashboard');
      } finally {
        this.loading = false;
      }
    },
    
    // Format currency
    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
      }).format(amount);
    },
    
    // Format relative time
    formatRelativeTime(days) {
      if (days === 0) return 'Today';
      if (days === 1) return 'Yesterday';
      if (days === 999) return 'Never';
      return `${days} days ago`;
    }
  }));
  
});