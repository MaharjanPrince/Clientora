// dashboard-status.js - Dashboard status/summary helpers
// The main dashboard rendering is handled by dashboardStats() in dashboard-page.js
// and rendered in dashboard.html via Alpine.js.

// Helper: returns a CSS class based on deal stage
function getDealStageBadgeClass(stage) {
  const map = {
    lead: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    proposal: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    negotiation: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    won: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    lost: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };
  return map[stage] || 'bg-gray-100 text-gray-800';
}

// Helper: format large numbers compactly
function compactNumber(n) {
  if (n >= 1000000) return `$${(n / 1000000).toFixed(1)}M`;
  if (n >= 1000) return `$${(n / 1000).toFixed(0)}K`;
  return `$${n}`;
}
