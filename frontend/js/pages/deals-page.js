// deals-page.js - Full deals page Alpine.js component (Kanban + List)
function dealsPage() {
  return {
    deals: [],
    contacts: [],
    loading: true,
    error: null,
    viewMode: 'kanban', // 'kanban' | 'list'

    // Modal state
    showModal: false,
    modalMode: 'create',
    saving: false,
    form: { title: '', contact_id: '', amount: '', stage: 'lead' },
    editingId: null,
    formError: null,

    // Delete confirm
    deleteConfirmId: null,

    // Drag state
    draggingDealId: null,

    stages: [
      { key: 'lead',        label: 'Lead',        color: 'yellow',  icon: '⚡' },
      { key: 'proposal',    label: 'Proposal',    color: 'blue',    icon: '📋' },
      { key: 'negotiation', label: 'Negotiation', color: 'purple',  icon: '🤝' },
      { key: 'won',         label: 'Won',         color: 'green',   icon: '🎉' },
      { key: 'lost',        label: 'Lost',        color: 'red',     icon: '✗'  },
    ],

    get dealsByStage() {
      const map = {};
      this.stages.forEach(s => { map[s.key] = []; });
      this.deals.forEach(d => {
        if (map[d.stage]) map[d.stage].push(d);
      });
      return map;
    },

    get totalPipeline() {
      return this.deals
        .filter(d => d.stage !== 'lost')
        .reduce((sum, d) => sum + parseFloat(d.amount || 0), 0);
    },

    get wonTotal() {
      return this.deals
        .filter(d => d.stage === 'won')
        .reduce((sum, d) => sum + parseFloat(d.amount || 0), 0);
    },

    stageTotal(stage) {
      return (this.dealsByStage[stage] || [])
        .reduce((sum, d) => sum + parseFloat(d.amount || 0), 0);
    },

    stageColor(key) {
      const s = this.stages.find(x => x.key === key);
      return s ? s.color : 'gray';
    },

    stageLabel(key) {
      const s = this.stages.find(x => x.key === key);
      return s ? s.label : key;
    },

    async init() {
      await Promise.all([this.loadDeals(), this.loadContacts()]);
    },

    async loadDeals() {
      this.loading = true;
      this.error = null;
      try {
        this.deals = await API.getDeals();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    async loadContacts() {
      try {
        this.contacts = await API.getContacts();
      } catch (e) {
        // contacts not critical for deals page load
      }
    },

    contactName(contactId) {
      const c = this.contacts.find(x => x.id === contactId);
      return c ? c.name : 'Unknown';
    },

    openCreateModal(stage = 'lead') {
      this.modalMode = 'create';
      this.form = { title: '', contact_id: '', amount: '', stage };
      this.editingId = null;
      this.formError = null;
      this.showModal = true;
    },

    openEditModal(deal) {
      this.modalMode = 'edit';
      this.form = {
        title: deal.title || '',
        contact_id: deal.contact_id || '',
        amount: deal.amount || '',
        stage: deal.stage || 'lead'
      };
      this.editingId = deal.id;
      this.formError = null;
      this.showModal = true;
    },

    closeModal() {
      this.showModal = false;
      this.formError = null;
    },

    async saveDeal() {
      this.saving = true;
      this.formError = null;
      try {
        const payload = {
          ...this.form,
          amount: parseFloat(this.form.amount)
        };
        if (this.modalMode === 'create') {
          const d = await API.createDeal(payload);
          this.deals.unshift(d);
          Alpine.store('toast').success(`Deal "${d.title}" created!`);
        } else {
          const updatePayload = {
            title: payload.title,
            amount: payload.amount,
            stage: payload.stage
          };
          const d = await API.updateDeal(this.editingId, updatePayload);
          const idx = this.deals.findIndex(x => x.id === this.editingId);
          if (idx !== -1) this.deals[idx] = d;
          Alpine.store('toast').success('Deal updated!');
        }
        this.showModal = false;
      } catch (e) {
        this.formError = e.message;
      } finally {
        this.saving = false;
      }
    },

    confirmDelete(id) {
      this.deleteConfirmId = id;
    },

    cancelDelete() {
      this.deleteConfirmId = null;
    },

    async deleteDeal(id) {
      try {
        await API.deleteDeal(id);
        this.deals = this.deals.filter(d => d.id !== id);
        this.deleteConfirmId = null;
        Alpine.store('toast').success('Deal deleted.');
      } catch (e) {
        Alpine.store('toast').error(e.message);
        this.deleteConfirmId = null;
      }
    },

    // Drag and drop handlers
    onDragStart(dealId) {
      this.draggingDealId = dealId;
    },

    onDragOver(e) {
      e.preventDefault();
    },

    async onDrop(e, targetStage) {
      e.preventDefault();
      if (!this.draggingDealId) return;
      const deal = this.deals.find(d => d.id === this.draggingDealId);
      if (!deal || deal.stage === targetStage) {
        this.draggingDealId = null;
        return;
      }
      try {
        const updated = await API.updateDeal(deal.id, { stage: targetStage });
        const idx = this.deals.findIndex(d => d.id === deal.id);
        if (idx !== -1) this.deals[idx] = updated;
        Alpine.store('toast').success(`Moved to ${this.stageLabel(targetStage)}`);
      } catch (e) {
        Alpine.store('toast').error('Failed to move deal');
      } finally {
        this.draggingDealId = null;
      }
    },

    formatCurrency(amount) {
      return new Intl.NumberFormat('en-US', {
        style: 'currency', currency: 'USD',
        minimumFractionDigits: 0, maximumFractionDigits: 0
      }).format(amount || 0);
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
      });
    }
  };
}

