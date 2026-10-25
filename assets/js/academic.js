(() => {
  const dialog = document.querySelector('.figure-dialog');
  if (!dialog || typeof dialog.showModal !== 'function') return;

  const fullImage = dialog.querySelector('.figure-full');
  const caption = dialog.querySelector('figcaption');
  let opener;
  let pointerStartedOutside = false;

  document.querySelectorAll('.paper-figure').forEach(link => {
    const image = link.querySelector('img');
    link.setAttribute('role', 'button');
    link.setAttribute('aria-haspopup', 'dialog');
    link.setAttribute('aria-label', `Enlarge: ${image.alt}`);
    link.addEventListener('click', event => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      opener = link;
      fullImage.src = image.src;
      fullImage.alt = image.alt;
      caption.textContent = link.closest('li').querySelector('.paper-title').textContent +
        (link.dataset.figureNote ? ` ${link.dataset.figureNote}` : '');
      document.documentElement.classList.add('figure-open');
      dialog.showModal();
    });
    link.addEventListener('keydown', event => {
      if (event.key === ' ') {
        event.preventDefault();
        link.click();
      }
    });
  });

  dialog.querySelector('.figure-close').addEventListener('click', () => dialog.close());
  const isOutside = event => {
    const bounds = dialog.getBoundingClientRect();
    return event.clientX < bounds.left || event.clientX > bounds.right ||
      event.clientY < bounds.top || event.clientY > bounds.bottom;
  };
  dialog.addEventListener('pointerdown', event => {
    pointerStartedOutside = isOutside(event);
  });
  dialog.addEventListener('click', event => {
    if (pointerStartedOutside && isOutside(event)) dialog.close();
    pointerStartedOutside = false;
  });
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('figure-open');
    opener?.focus({ preventScroll: true });
  });
})();
