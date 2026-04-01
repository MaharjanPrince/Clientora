// Conversation Analyzer Component
function conversationAnalyzer() {
  return {
    rawText: '',
    loading: false,
    error: null,
    insight: null,
    conversationId: null,

    async analyzeConversation() {
      if (!this.rawText.trim()) {
        Alpine.store('toast').error('Please paste a conversation first');
        return;
      }

      this.loading = true;
      this.error = null;
      this.insight = null;

      try {
        const response = await apiFetch('/conversations/analyze', {
          method: 'POST',
          body: JSON.stringify({ raw_text: this.rawText })
        });

        this.conversationId = response.conversation_id;
        this.insight = response.deal_insights;
        Alpine.store('toast').success('Conversation analyzed successfully!');
      } catch (err) {
        this.error = err.message || 'Failed to analyze conversation';
        Alpine.store('toast').error(this.error);
      } finally {
        this.loading = false;
      }
    },

    getStatusClass(status) {
      const s = (status || '').toLowerCase();
      if (s.includes('hot')) return 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300';
      if (s.includes('warm')) return 'bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300';
      if (s.includes('cold')) return 'bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300';
      return 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300';
    },

    parseSignalStrength(signal) {
      // Parse "3/5" format
      if (!signal) return { filled: 3, total: 5 };
      const match = signal.match(/(\d)\/(\d)/);
      if (match) {
        return { filled: parseInt(match[1]), total: parseInt(match[2]) };
      }
      return { filled: 3, total: 5 };
    },

    renderSignalDots(signal) {
      const { filled, total } = this.parseSignalStrength(signal);
      let dots = '';
      for (let i = 0; i < total; i++) {
        dots += i < filled ? '●' : '○';
      }
      return dots;
    },

    reset() {
      this.rawText = '';
      this.loading = false;
      this.error = null;
      this.insight = null;
      this.conversationId = null;
    },

    async setReminder() {
      // Placeholder - could integrate with calendar API
      Alpine.store('toast').info('Reminder feature coming soon!');
    },

    async draftFollowUp() {
      // Placeholder - could open email draft
      Alpine.store('toast').info('Draft email feature coming soon!');
    },

    async saveContact() {
      if (!this.insight) return;

      // Check if we have an email
      if (!this.insight.contact_email || !this.insight.contact_email.includes('@')) {
        Alpine.store('toast').error('Cannot save contact: No email found in conversation');
        return;
      }

      try {
        const contactData = {
          name: this.insight.contact_name || 'Unknown Contact',
          company_name: this.insight.company || null,
          email: this.insight.contact_email,
          phone_no: null
        };

        await API.createContact(contactData);
        await Alpine.store('data').refreshContacts();
        Alpine.store('toast').success('Contact saved successfully!');

        // Ask if they want to create a deal
        const createDeal = confirm('Contact saved! Would you like to create a deal for this opportunity?');
        if (createDeal) {
          // Store deal insights for the deals page to use
          Alpine.store('pendingDeal', {
            contactName: this.insight.contact_name,
            company: this.insight.company,
            summary: this.insight.summary,
            amount: null, // They can fill this in
            stage: this.insight.status?.includes('Hot') ? 'Proposal' : 'Discovery'
          });
          
          // Navigate to deals page
          Alpine.store('navigation').setPage('deals');
        }
      } catch (err) {
        Alpine.store('toast').error(err.message || 'Failed to save contact');
      }
    }
  };
}
