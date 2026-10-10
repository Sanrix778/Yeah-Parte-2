// Lector de comics (spec §7.3): índice flotante + atajos ← → y Esc.
export function initReader() {
  const pages = Array.from(document.querySelectorAll('[data-page]'));
  if (!pages.length) return;

  const index = document.querySelector('[data-page-index]');

  // Índice: click en un número desplaza a esa página.
  if (index) {
    index.addEventListener('click', (event) => {
      const btn = event.target.closest('[data-goto]');
      if (!btn) return;
      document.getElementById(btn.dataset.goto)?.scrollIntoView({
        behavior: 'smooth',
        block: 'start',
      });
    });
  }

  // Marca en el índice la página que se está leyendo.
  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const n = pages.indexOf(entry.target) + 1;
        for (const b of index?.querySelectorAll('[data-goto]') ?? []) {
          b.classList.toggle('devil-accent', b.dataset.goto === `page-${n}`);
        }
      }
    },
    { rootMargin: '-45% 0px -45% 0px' },
  );
  for (const page of pages) observer.observe(page);

  function currentIndex() {
    const mid = window.innerHeight / 2;
    let best = 0;
    pages.forEach((page, i) => {
      const rect = page.getBoundingClientRect();
      if (rect.top <= mid) best = i;
    });
    return best;
  }

  function go(delta) {
    const target = pages[currentIndex() + delta];
    target?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  document.addEventListener('keydown', (event) => {
    if (event.target.matches('input, textarea, select')) return;
    if (event.key === 'ArrowRight' || event.key === 'PageDown') {
      event.preventDefault();
      go(1);
    } else if (event.key === 'ArrowLeft' || event.key === 'PageUp') {
      event.preventDefault();
      go(-1);
    }
  });

  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    const back = document.querySelector('[data-page-index]');
    if (back) window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

if (document.readyState !== 'loading') initReader();
else document.addEventListener('DOMContentLoaded', initReader);