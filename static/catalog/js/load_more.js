document.addEventListener('DOMContentLoaded', function () {
  const loadBtn = document.getElementById('loadMoreBtn');
  if (!loadBtn || loadBtn.dataset.hasMore === 'false') {
    loadBtn?.remove();
    return;
  }

  loadBtn.addEventListener('click', function () {
    const offset = parseInt(loadBtn.dataset.offset || '0');
    fetch(`/?offset=${offset}`, {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(res => res.json())
    .then(data => {
      const grid = document.getElementById('productGrid');

      if (data.html?.trim()) {
        grid.insertAdjacentHTML('beforeend', data.html);
        loadBtn.dataset.offset = offset + 9;
      }

      loadBtn.dataset.hasMore = data.has_more ? 'true' : 'false';

      if (!data.has_more || !data.html.trim()) {
        loadBtn.remove();
        const noMoreBlock = document.getElementById('noMoreProducts');
        if (noMoreBlock) {
          noMoreBlock.style.display = 'block';
        }
      }
      
    })
    .catch(error => {
      console.error('Ошибка при загрузке товаров:', error);
      loadBtn.remove();
    });
  });
});
