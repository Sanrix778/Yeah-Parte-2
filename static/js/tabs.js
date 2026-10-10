// Tabs de la página de juego (spec §7.5).
// El servidor ya renderiza el panel correcto según ?tab=; esto solo evita que
// la navegación recargue la página. Sin JS, los links funcionan igual.
export function initTabs() {
  const buttons = document.querySelectorAll('[data-tab-btn]');
  const panels = document.querySelectorAll('[data-tab-panel]');
  if (!buttons.length || !panels.length) return;

  function activate(key) {
    for (const panel of panels) {
      panel.hidden = panel.dataset.tabPanel !== key;
    }
    for (const btn of buttons) {
      const active = btn.dataset.tabBtn === key;
      btn.setAttribute('aria-selected', String(active));
      btn.classList.toggle('devil-accent', active);
    }
  }

  for (const btn of buttons) {
    btn.addEventListener('click', (event) => {
      event.preventDefault();
      const key = btn.dataset.tabBtn;
      activate(key);
      history.replaceState(null, '', `?tab=${key}`);
    });
  }

  // Flechas del teclado entre tabs (patrón ARIA).
  buttons.forEach((btn, i) => {
    btn.addEventListener('keydown', (event) => {
      const delta = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
      if (!delta) return;
      event.preventDefault();
      const next = buttons[(i + delta + buttons.length) % buttons.length];
      next.focus();
      next.click();
    });
  });
}

if (document.readyState !== 'loading') initTabs();
else document.addEventListener('DOMContentLoaded', initTabs);