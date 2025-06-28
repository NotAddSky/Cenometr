document.addEventListener('DOMContentLoaded', function () {
    const setupFilter = (inputId, tableId) => {
      const input = document.getElementById(inputId);
      const table = document.getElementById(tableId);
      input.addEventListener('input', () => {
        const value = input.value.toLowerCase();
        table.querySelectorAll('tbody tr').forEach(row => {
          row.style.display = row.textContent.toLowerCase().includes(value) ? '' : 'none';
        });
      });
    };
  
    setupFilter('productSearch', 'productTable');
    setupFilter('categorySearch', 'categoryTable');
    setupFilter('manufacturerSearch', 'manufacturerTable');
  });
  