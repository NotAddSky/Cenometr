function fetchList(type, query = '', page = 1) {
  fetch(`/admin/fetch_${type}/?q=${query}&page=${page}`)
    .then(res => res.text())
    .then(html => {
      document.getElementById(`${type}Section`).innerHTML = html;
    });
}

document.addEventListener('DOMContentLoaded', () => {
  document.body.addEventListener('input', e => {
    if (e.target.id === 'productSearch') fetchList('products', e.target.value);
    if (e.target.id === 'manufacturerSearch') fetchList('manufacturers', e.target.value);
    if (e.target.id === 'categorySearch') fetchList('categories', e.target.value);
  });

  document.body.addEventListener('click', e => {
    if (e.target.classList.contains('page-link')) {
      const page = e.target.dataset.page;
      const section = e.target.closest('.tab-pane').id.replace('Tab', '').toLowerCase();
      const input = document.querySelector(`#${section}Search`);
      fetchList(section, input?.value || '', page);
    }
  });
});
