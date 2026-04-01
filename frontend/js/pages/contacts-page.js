// contacts-page.js - Full contacts page Alpine.js component
function contactsPage() {
  return {
    contacts: [],
    loading: true,
    error: null,
    search: '',

    // Modal state
    showModal: false,
    modalMode: 'create', // 'create' | 'edit'
    saving: false,
    form: { name: '', email: '', phone_no: '', company_name: '' },
    editingId: null,
    formError: null,

    // Detail panel state
    selectedContact: null,
    detailLoading: false,
    notes: [],
    notesLoading: false,
    showNoteForm: false,
    noteForm: { title: '', content: '' },
    savingNote: false,
    aiContext: null,
    aiLoading: false,
    activeTab: 'notes', // 'notes' | 'ai'

    // Delete confirm
    deleteConfirmId: null,

    get filteredContacts() {
      if (!this.search.trim()) return this.contacts;
      const q = this.search.toLowerCase();
      return this.contacts.filter(c =>
        (c.name || '').toLowerCase().includes(q) ||
        (c.email || '').toLowerCase().includes(q) ||
        (c.company_name || '').toLowerCase().includes(q) ||
        (c.phone_no || '').toLowerCase().includes(q)
      );
    },

    async init() {
      await this.loadContacts();
      
      // Listen for contact updates from analyzer or other sources
      window.addEventListener('contacts-updated', (e) => {
        this.contacts = e.detail;
      });
    },

    async loadContacts() {
      this.loading = true;
      this.error = null;
      try {
        this.contacts = await API.getContacts();
      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    },

    openCreateModal() {
      this.modalMode = 'create';
      this.form = { name: '', email: '', phone_no: '', company_name: '' };
      this.editingId = null;
      this.formError = null;
      this.showModal = true;
    },

    openEditModal(contact) {
      this.modalMode = 'edit';
      this.form = {
        name: contact.name || '',
        email: contact.email || '',
        phone_no: contact.phone_no || '',
        company_name: contact.company_name || ''
      };
      this.editingId = contact.id;
      this.formError = null;
      this.showModal = true;
    },

    closeModal() {
      this.showModal = false;
      this.formError = null;
    },

    async saveContact() {
      this.saving = true;
      this.formError = null;
      try {
        if (this.modalMode === 'create') {
          const c = await API.createContact(this.form);
          this.contacts.unshift(c);
          // Sync to global store so deals page sees it immediately
          Alpine.store('data').contacts.unshift(c);
          Alpine.store('toast').success(`${c.name} added!`);
        } else {
          const c = await API.updateContact(this.editingId, this.form);
          const idx = this.contacts.findIndex(x => x.id === this.editingId);
          if (idx !== -1) this.contacts[idx] = c;
          if (this.selectedContact?.id === this.editingId) this.selectedContact = c;
          // Sync to global store
          const storeIdx = Alpine.store('data').contacts.findIndex(x => x.id === this.editingId);
          if (storeIdx !== -1) Alpine.store('data').contacts[storeIdx] = c;
          Alpine.store('toast').success('Contact updated!');
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

    async deleteContact(id) {
      try {
        await API.deleteContact(id);
        this.contacts = this.contacts.filter(c => c.id !== id);
        if (this.selectedContact?.id === id) this.selectedContact = null;
        this.deleteConfirmId = null;
        // Sync to global store
        Alpine.store('data').contacts = Alpine.store('data').contacts.filter(c => c.id !== id);
        Alpine.store('toast').success('Contact deleted.');
      } catch (e) {
        Alpine.store('toast').error(e.message);
        this.deleteConfirmId = null;
      }
    },

    async selectContact(contact) {
      this.selectedContact = contact;
      this.notes = [];
      this.aiContext = null;
      this.activeTab = 'notes';
      this.showNoteForm = false;
      await this.loadNotes(contact.id);
    },

    async loadNotes(contactId) {
      this.notesLoading = true;
      try {
        this.notes = await API.getNotes(contactId);
      } catch (e) {
        Alpine.store('toast').error('Failed to load notes');
      } finally {
        this.notesLoading = false;
      }
    },

    async addNote() {
      if (!this.noteForm.title.trim() || !this.noteForm.content.trim()) return;
      this.savingNote = true;
      try {
        const note = await API.createNote(this.selectedContact.id, this.noteForm);
        this.notes.unshift(note);
        this.noteForm = { title: '', content: '' };
        this.showNoteForm = false;
        Alpine.store('toast').success('Note added!');
      } catch (e) {
        Alpine.store('toast').error(e.message);
      } finally {
        this.savingNote = false;
      }
    },

    async loadAIContext() {
      this.aiLoading = true;
      this.aiContext = null;
      try {
        this.aiContext = await API.getContactContext(this.selectedContact.id);
      } catch (e) {
        Alpine.store('toast').error('AI context failed: ' + e.message);
      } finally {
        this.aiLoading = false;
      }
    },

    async switchTab(tab) {
      this.activeTab = tab;
      if (tab === 'ai' && !this.aiContext && this.selectedContact) {
        await this.loadAIContext();
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return '';
      return new Date(dateStr).toLocaleDateString('en-US', {
        month: 'short', day: 'numeric', year: 'numeric'
      });
    },

    getInitials(name) {
      return (name || '?').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
    },

    getAvatarColor(name) {
      const colors = ['#6366f1','#8b5cf6','#ec4899','#f59e0b','#10b981','#3b82f6','#ef4444','#14b8a6'];
      let hash = 0;
      for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
      return colors[Math.abs(hash) % colors.length];
    }
  };
}