document.getElementById('addressSelect').addEventListener('change', function () {
  const addressId = this.value;
  const storeList = document.getElementById('storeList');

  if (!addressId) {
    // Если выбран "все адреса" — подгружаем товары заново
    fetch('/?offset=0', {
      headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
      .then(res => res.json())
      .then(data => {
        document.getElementById('productGrid').innerHTML = data.html;
        document.getElementById('loadMoreBtn').dataset.offset = 9;
        storeList.innerHTML = '';
        storeList.style.display = 'none';
      });
    return;
  }

  // В остальных случаях — подгружаем магазины
  fetch(`/api/stores/by-address/${addressId}/`)
    .then(res => res.json())
    .then(data => {
      storeList.innerHTML = '';
      data.stores.forEach(store => {
        const btn = document.createElement('button');
        btn.className = 'list-group-item list-group-item-action';
        btn.textContent = store.name;
        btn.onclick = () => loadProductsByStore(store.id);
        storeList.appendChild(btn);
      });
      storeList.style.display = 'block';
    });
});

function loadProductsByStore(storeId) {
  fetch(`/api/products/by-store/${storeId}/`)
    .then(res => res.json())
    .then(data => {
      document.getElementById('productGrid').innerHTML = data.html;
      document.getElementById('loadMoreBtn').style.display = 'none';
    });
}
