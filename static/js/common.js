async function loadConfig(ids = ['newsDays', 'newsDaysHero']) {
  try {
    const res = await fetch('/api/config');
    if (!res.ok) return;
    const cfg = await res.json();
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.textContent = cfg.news_days;
    });
  } catch (_) {}
}

window.addEventListener('focus', () => loadConfig());

function showStatus(el, msg, type) {
  el.textContent = msg;
  el.className = 'status show ' + (type || '');
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
