(() => {
  'use strict';
  const root = document.documentElement;
  const systemTheme = matchMedia('(prefers-color-scheme: dark)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const themeButton = document.querySelector('.theme-toggle');
  const currentTheme = () => root.dataset.theme || (systemTheme.matches ? 'dark' : 'light');
  function updateThemeControl() {
    const dark = currentTheme() === 'dark';
    if (themeButton) {
      themeButton.setAttribute('aria-label', `Switch to ${dark ? 'light' : 'dark'} theme`);
      themeButton.innerHTML = dark
        ? '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/></svg>'
        : '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.5 14.5A8.5 8.5 0 0 1 9.5 3.5a8.5 8.5 0 1 0 11 11Z"/></svg>';
    }
    document.querySelector('meta[name="theme-color"]')?.setAttribute('content', dark ? '#0c1c21' : '#f5f5f0');
  }
  if (themeButton) {
    themeButton.hidden = false;
    themeButton.addEventListener('click', () => {
      root.dataset.theme = currentTheme() === 'dark' ? 'light' : 'dark';
      try { localStorage.setItem('theme', root.dataset.theme); } catch (_) {}
      updateThemeControl();
    });
  }
  updateThemeControl();
  systemTheme.addEventListener('change', updateThemeControl);
  window.addEventListener('storage', event => {
    if (event.key !== 'theme') return;
    if (event.newValue === 'light' || event.newValue === 'dark') root.dataset.theme = event.newValue;
    else delete root.dataset.theme;
    updateThemeControl();
  });

  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('.primary-nav');
  if (menu && nav) {
    const setMenu = open => {
      nav.classList.toggle('is-open', open);
      menu.setAttribute('aria-expanded', String(open));
      menu.textContent = open ? 'Close' : 'Menu';
    };
    menu.addEventListener('click', () => setMenu(menu.getAttribute('aria-expanded') !== 'true'));
    nav.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link) return;
      setMenu(false);
      if (getComputedStyle(menu).display !== 'none' && link.hash && link.pathname === location.pathname) {
        const target = document.getElementById(link.hash.slice(1));
        if (target) {
          target.tabIndex = -1;
          target.focus({ preventScroll: true });
          target.addEventListener('blur', () => target.removeAttribute('tabindex'), { once: true });
        }
      }
    });
    document.addEventListener('keydown', event => {
      if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        menu.focus();
      }
    });
    matchMedia('(min-width: 801px)').addEventListener('change', () => setMenu(false));
  }
  // Only collapse the mobile navigation once its controls have been installed.
  root.classList.add('js');

  const anchorLinks = [...document.querySelectorAll('.primary-nav a[href^="#"]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        anchorLinks.forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-15% 0px -70% 0px' });
    anchorLinks.forEach(link => {
      const section = document.getElementById(link.hash.slice(1));
      if (section) observer.observe(section);
    });
  }

  // Animations autoplay muted and loop from first load, as the owner requested.
  // Sources stay in data-src until reduced motion has been checked, so a
  // reduced-motion visitor keeps the static poster and never loads the MP4.
  const media = [...document.querySelectorAll('[data-autoplay-media]')].map(figure => {
    const video = figure.querySelector('video');
    const still = figure.querySelector('img');
    if (!video || !video.dataset.src) return null;
    let run = 0;
    const showPoster = () => {
      run++;
      video.pause();
      video.hidden = true;
      still?.removeAttribute('aria-hidden');
    };
    const start = () => {
      const current = ++run;
      video.muted = true;
      if (!video.getAttribute('src')) video.src = video.dataset.src;
      else video.currentTime = 0;
      video.hidden = false;
      // The poster image stays underneath for sizing; announce only the video.
      still?.setAttribute('aria-hidden', 'true');
      video.play()?.catch(() => { if (current === run) showPoster(); });
    };
    video.addEventListener('error', showPoster);
    return { start, showPoster };
  }).filter(Boolean);
  const applyMotion = () => media.forEach(item => reducedMotion.matches ? item.showPoster() : item.start());
  applyMotion();
  reducedMotion.addEventListener('change', applyMotion);
})();
