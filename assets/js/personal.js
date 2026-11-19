(() => {
  const name = document.querySelector('.name-heading');
  // Letter markup is rendered in HTML so its first animation never waits for JS.
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = window.matchMedia('(hover: hover) and (pointer: fine)');
  // Pair the plain-language ambition with its research areas in both directions.
  const focusLinks = [...document.querySelectorAll('.slogan-focus, .interest-link')];
  const focusSurfaces = [...document.querySelectorAll('.slogan-focus, .interests li[data-focus-group]')];
  let hoveredGroup = null;
  function updateResearchFocus() {
    const focusedGroup = document.activeElement?.closest('a[data-focus-group]')?.dataset.focusGroup;
    const group = hoveredGroup || focusedGroup;
    focusSurfaces.forEach(element => element.classList.toggle('is-linked', Boolean(group) && element.dataset.focusGroup === group));
  }
  focusLinks.forEach(link => {
    link.addEventListener('pointerenter', event => {
      if (event.pointerType === 'touch') return;
      hoveredGroup = link.dataset.focusGroup;
      updateResearchFocus();
    });
    link.addEventListener('pointerleave', () => { hoveredGroup = null; updateResearchFocus(); });
    link.addEventListener('focus', updateResearchFocus);
    link.addEventListener('blur', () => requestAnimationFrame(updateResearchFocus));
    link.addEventListener('click', event => {
      if (event.button !== 0 || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      const destination = document.getElementById(link.hash.slice(1));
      const focusTarget = destination?.matches('a') ? destination : destination?.querySelector('a');
      if (!focusTarget) return;
      event.preventDefault();
      hoveredGroup = null;
      focusTarget.focus({ preventScroll: true });
      const bounds = destination.getBoundingClientRect();
      const headerBottom = document.querySelector('.masthead').getBoundingClientRect().bottom;
      if (bounds.top < headerBottom + 20 || bounds.bottom > innerHeight - 24) {
        destination.scrollIntoView({ behavior: reducedMotion.matches ? 'auto' : 'smooth', block: 'center' });
      }
      updateResearchFocus();
    });
  });
  const portrait = document.querySelector('.portrait-frame');
  const inkLetters = [...document.querySelectorAll('.glyph-ink')];
  let nameFrame = 0;
  let portraitFrame = 0;
  let namePointer;
  let portraitPointer;
  function resetName() {
    cancelAnimationFrame(nameFrame);
    nameFrame = 0;
    inkLetters.forEach(letter => {
      letter.style.removeProperty('--letter-ink');
      letter.style.removeProperty('--letter-lift');
    });
  }
  function resetPortrait() {
    cancelAnimationFrame(portraitFrame);
    portraitFrame = 0;
    portrait?.style.removeProperty('--tilt-x');
    portrait?.style.removeProperty('--tilt-y');
  }
  name?.addEventListener('pointermove', event => {
    if (reducedMotion.matches || !finePointer.matches) return;
    namePointer = { x: event.clientX, y: event.clientY };
    if (nameFrame) return;
    nameFrame = requestAnimationFrame(() => {
      nameFrame = 0;
      // Read every box before changing styles: no read/write layout loop per letter.
      const boxes = inkLetters.map(letter => letter.getBoundingClientRect());
      inkLetters.forEach((letter, index) => {
        const bounds = boxes[index];
        const distance = Math.hypot(namePointer.x - bounds.left - bounds.width / 2,
          (namePointer.y - bounds.top - bounds.height / 2) * .65);
        const proximity = Math.max(0, 1 - distance / 115);
        const blend = (from, to) => Math.round(from + (to - from) * proximity);
        letter.style.setProperty('--letter-ink', `rgb(${blend(48,196)} ${blend(41,18)} ${blend(44,48)})`);
        letter.style.setProperty('--letter-lift', `${(-3 * proximity).toFixed(2)}px`);
      });
    });
  });
  name?.addEventListener('pointerleave', resetName);
  portrait?.addEventListener('pointermove', event => {
    if (reducedMotion.matches || !finePointer.matches) return;
    portraitPointer = { x: event.clientX, y: event.clientY };
    if (portraitFrame) return;
    portraitFrame = requestAnimationFrame(() => {
      portraitFrame = 0;
      const bounds = portrait.parentElement.getBoundingClientRect();
      const x = Math.max(-.5, Math.min(.5, (portraitPointer.x - bounds.left) / bounds.width - .5));
      const y = Math.max(-.5, Math.min(.5, (portraitPointer.y - bounds.top) / bounds.height - .5));
      portrait.style.setProperty('--tilt-x', `${(-y * 4).toFixed(2)}deg`);
      portrait.style.setProperty('--tilt-y', `${(x * 4).toFixed(2)}deg`);
    });
  });
  portrait?.addEventListener('pointerleave', resetPortrait);
  reducedMotion.addEventListener('change', () => { resetName(); resetPortrait(); });
  finePointer.addEventListener('change', () => { resetName(); resetPortrait(); });
  const replay = document.querySelector('.replay-intro');
  replay?.addEventListener('click', () => {
    if (reducedMotion.matches) return;
    resetName();
    resetPortrait();
    // Replay the existing CSS timelines, including pseudo-elements, without a forced reflow.
    document.querySelectorAll('.sidebar, .intro').forEach(root => {
      root.getAnimations({ subtree: true }).forEach(animation => {
        if (!(animation instanceof CSSAnimation)) return;
        animation.currentTime = 0;
        animation.play();
      });
    });
  });
  if ('IntersectionObserver' in window && !reducedMotion.matches) {
    const entries = document.querySelectorAll('.publication-list > li');
    document.body.classList.add('has-reveals');
    const observer = new IntersectionObserver(changes => changes.forEach(change => {
      if (change.isIntersecting) {
        change.target.classList.remove('awaiting-reveal');
        observer.unobserve(change.target);
      }
    }), { threshold: 0.06 });
    // Late JS must never hide and re-animate content the visitor already sees.
    // Read positions first; only future, below-viewport entries need a reveal.
    const upcoming = [...entries].filter(entry => entry.getBoundingClientRect().top >= innerHeight);
    upcoming.forEach(entry => { entry.classList.add('awaiting-reveal'); observer.observe(entry); });
  }
  const navLinks = [...document.querySelectorAll('.nav-links a[href^="#"]')];
  const sections = navLinks.map(link => document.querySelector(link.hash));
  const progress = document.querySelector('.reading-progress');
  let scheduled = false;
  let activeId;
  function update() {
    const viewportHeight = window.innerHeight;
    const scrollTop = window.scrollY;
    const documentHeight = document.documentElement.scrollHeight;
    const threshold = viewportHeight * .35;
    let active = sections[0];
    sections.forEach(section => { if (section.getBoundingClientRect().top <= threshold) active = section; });
    if (scrollTop + viewportHeight >= documentHeight - 3) active = sections[sections.length - 1];
    // Complete all geometry reads before writing navigation/progress styles.
    if (active.id !== activeId) {
      activeId = active.id;
      navLinks.forEach(link => {
        if (link.hash === '#' + activeId) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }
    const distance = documentHeight - viewportHeight;
    progress.style.transform = `scaleX(${distance > 0 ? Math.min(1, Math.max(0, scrollTop / distance)) : 0})`;
    scheduled = false;
  }
  function schedule() { if (!scheduled) { scheduled = true; requestAnimationFrame(update); } }
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  update();
})();
