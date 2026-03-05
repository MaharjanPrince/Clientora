// dashboard-page.js - Dashboard stats component
function dashboardStats() {
  return {
    dashboard: null,
    loading: true,
    error: null,

    async init() {
      await this.fetchDashboard();
    },

    async fetchDashboard() {
      this.loading = true;
      this.error = null;
      try {
        this.dashboard = await API.getDashboard();
      } catch (error) {
        this.error = error.message;
      } finally {
        this.loading = false;
      }
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD',
        minimumFractionDigits: 0, maximumFractionDigits: 0
      }).format(amount || 0);
    },

    formatRelativeTime(days) {
      if (days === 0) return 'Today';
      if (days === 1) return 'Yesterday';
      if (days === 999) return 'Never contacted';
      return `${days} days ago`;
    }
  };
}

