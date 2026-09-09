// Run before styles are painted. Keep the existing site's `theme` preference.
(() => {
  try {
    const theme = localStorage.getItem('theme');
    if (theme === 'dark' || theme === 'light') document.documentElement.dataset.theme = theme;
  } catch (_) { /* System preference remains available when storage is blocked. */ }
})();
