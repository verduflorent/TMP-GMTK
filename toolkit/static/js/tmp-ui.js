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
