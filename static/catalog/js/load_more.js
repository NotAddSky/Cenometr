document.addEventListener('DOMContentLoaded', function () {
  const loadMoreBtn = document.getElementById('loadMoreBtn');
  if (!loadMoreBtn) return;

  loadMoreBtn.addEventListener('click', function () {
    const offset = parseInt(loadMoreBtn.dataset.offset, 10);

    fetch(`/?offset=${offset}`, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Ошибка загрузки данных');
        }
        return response.json();
      })
      .then(data => {
        if (data.html) {
          const productGrid = document.getElementById('productGrid');
          productGrid.insertAdjacentHTML('beforeend', data.html);
          // Увеличить offset
          loadMoreBtn.dataset.offset = offset + 9;
        } else {
          loadMoreBtn.remove(); // Если товаров больше нет
        }
      })
      .catch(error => {
        console.error("Ошибка подгрузки:", error);
      });
  });
});

document.addEventListener('DOMContentLoaded', () => {
  const filterForm = document.getElementById('productFilters');
  const categorySelect = document.getElementById('categorySelect');

  if (categorySelect) {
    categorySelect.addEventListener('change', () => {
      const category = categorySelect.value;
      const url = `/?category=${category}`;

      fetch(url, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
      .then(res => res.json())
      .then(data => {
        document.getElementById('productGrid').innerHTML = data.html;
        document.getElementById('loadMoreBtn').style.display = 'none';
      })
      .catch(err => console.error("Ошибка фильтрации:", err));
    });
  }
});
