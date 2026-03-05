// contacts-table.js - Re-exported as Alpine-compatible helper
// This file is kept for compatibility. The full contacts table logic
// is handled by the contactsPage() function in js/pages/contacts-page.js
// and rendered directly in dashboard.html via Alpine.js x-data directives.

// Utility: get avatar color from name string
function getContactAvatarColor(name) {
  const colors = ['#6366f1','#8b5cf6','#ec4899','#f59e0b','#10b981','#3b82f6'];
  let hash = 0;
  for (let i = 0; i < (name || '').length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return colors[Math.abs(hash) % colors.length];
}

// Utility: get initials from full name
function getContactInitials(name) {
  return (name || '?').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
}
