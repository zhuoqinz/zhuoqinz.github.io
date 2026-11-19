(() => {
  const preview = document.querySelector('.cv-preview');
  const button = document.querySelector('.cv-zoom');
  const viewport = document.querySelector('.cv-sheet-viewport');
  if (!preview || !button || !viewport) return;
  document.documentElement.classList.add('cv-enhanced');
  button.addEventListener('click', () => {
    const enlarged = preview.dataset.zoomed !== 'true';
    preview.dataset.zoomed = String(enlarged);
    button.setAttribute('aria-pressed', String(enlarged));
    button.querySelector('span').textContent = enlarged ? 'Fit to page' : 'Enlarge preview';
    if (!enlarged) viewport.scrollLeft = 0;
  });
})();
