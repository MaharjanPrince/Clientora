// dashboard-page.js - Dashboard stats component
function dashboardStats() {
  return {
    dashboard: {
      total_pipeline_value: 0,
      deals_by_stage: { lead: {count:0, total_value:0}, proposal: {count:0, total_value:0}, negotiation: {count:0, total_value:0}, won: {count:0, total_value:0}, lost: {count:0, total_value:0} },
      contacts_needing_followup: [],
      recent_activity: []
    },
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