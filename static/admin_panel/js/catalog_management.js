document.addEventListener('DOMContentLoaded', () => {
    loadProducts();
    loadCategories();
    loadManufacturers();
  
    // Поиск
    document.getElementById('productSearch').addEventListener('input', loadProducts);
    document.getElementById('categorySearch').addEventListener('input', loadCategories);
    document.getElementById('manufacturerSearch').addEventListener('input', loadManufacturers);
  });
  
  // ========== ТОВАРЫ ==========
  function loadProducts() {
    const search = document.getElementById('productSearch').value;
    fetch(`/admin/fetch_products/?search=${encodeURIComponent(search)}`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('productTableContainer');
        container.innerHTML = '';
  
        if (data.products.length === 0) {
          container.innerHTML = '<p class="text-muted">Нет товаров.</p>';
          return;
        }
  
        const table = document.createElement('table');
        table.className = 'table table-sm table-hover align-middle';
        table.innerHTML = `
          <thead><tr>
            <th>Название</th>
            <th>Категория</th>
            <th>Производитель</th>
            <th>Действия</th>
          </tr></thead>
          <tbody>
            ${data.products.map(p => `
              <tr>
                <td>${p.name}</td>
                <td>${p.category_name}</td>
                <td>${p.manufacturer_name}</td>
                <td>
                  <button class="btn btn-sm btn-outline-secondary me-2 edit-product" data-id="${p.id}">Редактировать</button>
                  <button class="btn btn-sm btn-outline-danger delete-product" data-id="${p.id}">Удалить</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        `;
        container.appendChild(table);
      });
  }
  
  // ========== КАТЕГОРИИ ==========
  function loadCategories() {
    const search = document.getElementById('categorySearch').value;
    fetch(`/admin/fetch_categories/?search=${encodeURIComponent(search)}`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('categoryTableContainer');
        container.innerHTML = '';
  
        if (data.categories.length === 0) {
          container.innerHTML = '<p class="text-muted">Нет категорий.</p>';
          return;
        }
  
        const table = document.createElement('table');
        table.className = 'table table-sm table-hover';
        table.innerHTML = `
          <thead><tr><th>Название</th><th>Действия</th></tr></thead>
          <tbody>
            ${data.categories.map(c => `
              <tr>
                <td>${c.name}</td>
                <td>
                  <button class="btn btn-sm btn-outline-secondary me-2 edit-category" data-id="${c.id}" data-name="${c.name}">Редактировать</button>
                  <button class="btn btn-sm btn-outline-danger delete-category" data-id="${c.id}">Удалить</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        `;
        container.appendChild(table);
      });
  }
  
  // ========== ПРОИЗВОДИТЕЛИ ==========
  function loadManufacturers() {
    const search = document.getElementById('manufacturerSearch').value;
    fetch(`/admin/fetch_manufacturers/?search=${encodeURIComponent(search)}`)
      .then(res => res.json())
      .then(data => {
        const container = document.getElementById('manufacturerTableContainer');
        container.innerHTML = '';
  
        if (data.manufacturers.length === 0) {
          container.innerHTML = '<p class="text-muted">Нет производителей.</p>';
          return;
        }
  
        const table = document.createElement('table');
        table.className = 'table table-sm table-hover';
        table.innerHTML = `
          <thead><tr><th>Название</th><th>Действия</th></tr></thead>
          <tbody>
            ${data.manufacturers.map(m => `
              <tr>
                <td>${m.name}</td>
                <td>
                  <button class="btn btn-sm btn-outline-secondary me-2 edit-manufacturer" data-id="${m.id}" data-name="${m.name}">Редактировать</button>
                  <button class="btn btn-sm btn-outline-danger delete-manufacturer" data-id="${m.id}">Удалить</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        `;
        container.appendChild(table);
      });
  }
  