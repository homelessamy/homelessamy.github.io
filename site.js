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

  // A real static figure is always present. No video URL is fetched until play.
  const media = [...document.querySelectorAll('[data-scientific-media]')].map(figure => {
    const video = figure.querySelector('video');
    const button = figure.querySelector('.media-toggle');
    if (!video || !button) return null;
    const playLabel = button.textContent;
    button.hidden = false;
    const sync = () => {
      button.setAttribute('aria-pressed', String(!video.paused));
      button.textContent = video.paused ? playLabel : 'Pause visualization';
    };
    const showPoster = () => { video.pause(); video.hidden = true; sync(); };
    video.addEventListener('play', sync);
    video.addEventListener('pause', sync);
    video.addEventListener('error', () => {
      showPoster(); button.disabled = true; button.textContent = 'Video unavailable · still shown';
    });
    button.addEventListener('click', async () => {
      if (!video.paused) { video.pause(); return; }
      media.forEach(item => { if (item && item.video !== video) item.video.pause(); });
      if (!video.src) video.src = video.dataset.src;
      video.hidden = false;
      button.disabled = true;
      try { await video.play(); }
      catch (_) { showPoster(); }
      finally { button.disabled = false; sync(); }
    });
    if ('IntersectionObserver' in window) {
      new IntersectionObserver(entries => {
        if (!entries[0].isIntersecting) video.pause();
      }).observe(figure);
    }
    return { video, showPoster };
  });
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) media.forEach(item => item?.video.pause());
  });
  reducedMotion.addEventListener('change', () => {
    if (reducedMotion.matches) media.forEach(item => item?.showPoster());
  });

  // Preserve the contribution visualization and six-hour cache, load near it.
  const activity = document.getElementById('activity');
  if (!activity) return;
  const CACHE = 'gh-contrib-v1';
  const TTL = 6 * 60 * 60 * 1000;
  function valid(data) {
    return data && Array.isArray(data.contributions) && data.contributions.length > 0 &&
      data.contributions.every(day => /^\d{4}-\d{2}-\d{2}$/.test(day.date) &&
        Number.isInteger(day.level) && day.level >= 0 && day.level <= 4 &&
        Number.isInteger(day.count) && day.count >= 0);
  }
  function render(data) {
    const days = [...data.contributions].sort((a, b) => a.date.localeCompare(b.date)).slice(-366);
    const grid = document.getElementById('heatmap');
    grid.replaceChildren();
    const fragment = document.createDocumentFragment();
    const padding = new Date(`${days[0].date}T00:00:00Z`).getUTCDay();
    for (let i = 0; i < padding; i++) {
      const blank = document.createElement('i'); blank.style.visibility = 'hidden'; fragment.append(blank);
    }
    days.forEach(day => {
      const cell = document.createElement('i');
      cell.dataset.level = String(day.level);
      cell.title = `${day.count} contributions on ${day.date}`;
      fragment.append(cell);
    });
    grid.append(fragment);
    const total = days.reduce((sum, day) => sum + day.count, 0);
    const summary = `${total.toLocaleString()} contributions · ${days[0].date} to ${days.at(-1).date}`;
    grid.setAttribute('aria-label', summary);
    document.getElementById('activity-total').replaceChildren(document.createTextNode(`${total.toLocaleString()} contributions in the last year · `));
    const profile = document.createElement('a'); profile.href = 'https://github.com/homelessamy'; profile.textContent = '@homelessamy';
    document.getElementById('activity-total').append(profile);
    document.getElementById('heatmap-scroll').hidden = false;
    document.getElementById('heatmap-key').hidden = false;
    document.getElementById('activity-fallback').hidden = true;
  }
  async function loadActivity() {
    try {
      const cached = JSON.parse(localStorage.getItem(CACHE));
      if (cached && Date.now() - cached.t < TTL && valid(cached.d)) { render(cached.d); return; }
    } catch (_) {}
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 8000);
    try {
      const response = await fetch('https://github-contributions-api.jogruber.de/v4/homelessamy?y=last', { signal: controller.signal });
      if (!response.ok) throw new Error('Unavailable');
      const data = await response.json();
      if (!valid(data)) throw new Error('Invalid contribution history');
      render(data);
      try { localStorage.setItem(CACHE, JSON.stringify({ t: Date.now(), d: data })); } catch (_) {}
    } catch (_) { /* The profile link remains useful offline or during API outages. */ }
    finally { clearTimeout(timeout); }
  }
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { observer.disconnect(); loadActivity(); }
    }, { rootMargin: '300px' });
    observer.observe(activity);
  } else loadActivity();
})();
