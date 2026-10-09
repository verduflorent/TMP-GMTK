/* Visual feedback only. Rolls and resources remain owned by existing Django actions. */
document.querySelector('#compact-view')?.addEventListener('click', event => {
  const compact = document.querySelector('.table-combat').classList.toggle('is-compact');
  event.currentTarget.setAttribute('aria-pressed', String(compact));
  event.currentTarget.textContent = compact ? 'Vue détaillée' : 'Vue compacte';
});
const dock = document.querySelector('.dice-dock');
let rollTimeout;
dock?.querySelector('form').addEventListener('submit', () => {
  dock.classList.remove('is-perfect');
  dock.classList.add('is-rolling');
  clearTimeout(rollTimeout);
  rollTimeout = setTimeout(() => dock.classList.remove('is-rolling'), 1800);
});
window.addEventListener('tmp:roll', event => {
  if (!dock) return;
  clearTimeout(rollTimeout);
  dock.classList.remove('is-rolling');
  dock.classList.toggle('is-perfect', Number(event.detail.roll) === 1);
  dock.querySelector('output').textContent = event.detail.roll;
});
if (dock) dock.classList.toggle('is-perfect', Number(dock.querySelector('output').textContent.trim()) === 1);

/* Zoom only the combat card region; preserve dialogs, dice dock and page UI. */
(() => {
  const combat = document.querySelector('.table-combat');
  const output = document.getElementById('table-zoom-value');
  if (!combat || !output) return;
  const min = 60, max = 150, step = 10;
  let zoom = 100;
  try {
    const saved = Number(window.localStorage.getItem('tmp-combat-card-zoom'));
    if (Number.isFinite(saved) && saved >= min && saved <= max) zoom = saved;
  } catch (_) { /* Storage can be disabled. */ }
  const apply = () => {
    combat.style.setProperty('--combat-zoom', String(zoom / 100));
    output.textContent = zoom + ' %';
    document.getElementById('table-zoom-out').disabled = zoom <= min;
    document.getElementById('table-zoom-in').disabled = zoom >= max;
    try { window.localStorage.setItem('tmp-combat-card-zoom', String(zoom)); } catch (_) {}
  };
  document.getElementById('table-zoom-out').addEventListener('click', () => { zoom = Math.max(min, zoom - step); apply(); });
  document.getElementById('table-zoom-in').addEventListener('click', () => { zoom = Math.min(max, zoom + step); apply(); });
  document.getElementById('table-zoom-reset').addEventListener('click', () => { zoom = 100; apply(); });
  apply();
})();
