
(function () {
  const grid = document.getElementById('projectGrid');
  if (!grid) return;

  const cards = Array.from(grid.querySelectorAll('.project-card-v2'));
  const search = document.getElementById('projectSearch');
  const sort = document.getElementById('projectSort');
  const empty = document.getElementById('projectEmpty');
  const clear = document.getElementById('clearProjectSearch');
  const chips = Array.from(document.querySelectorAll('.project-chip'));

  let activeFilter = 'all';

  function apply() {
    const term = (search.value || '').trim().toLowerCase();

    cards.sort((a, b) => {
      if (sort.value === 'za') return b.dataset.name.localeCompare(a.dataset.name, 'es');
      if (sort.value === 'new') return (b.dataset.date || '').localeCompare(a.dataset.date || '');
      return a.dataset.name.localeCompare(b.dataset.name, 'es');
    });

    cards.forEach(card => grid.appendChild(card));

    let visible = 0;
    cards.forEach(card => {
      const matchesText = !term || card.dataset.search.includes(term);
      const matchesFilter = activeFilter === 'all' || card.dataset.modalidad === activeFilter;
      const show = matchesText && matchesFilter;
      card.hidden = !show;
      if (show) visible++;
    });

    empty.hidden = visible !== 0;
  }

  search.addEventListener('input', apply);
  sort.addEventListener('change', apply);

  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('is-active'));
      chip.classList.add('is-active');
      activeFilter = chip.dataset.filter || 'all';
      apply();
    });
  });

  clear.addEventListener('click', () => {
    search.value = '';
    activeFilter = 'all';
    chips.forEach(c => c.classList.toggle('is-active', c.dataset.filter === 'all'));
    apply();
    search.focus();
  });

  apply();
})();
