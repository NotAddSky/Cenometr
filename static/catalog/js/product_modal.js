document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.open-product-modal').forEach(button => {
      button.addEventListener('click', function () {
        const url = this.dataset.url;
        const productId = this.dataset.productId;
        const modal = new bootstrap.Modal(document.getElementById('productModal'));
        const modalContent = document.getElementById('productModalContent');
  
        modalContent.setAttribute('data-product-id', productId);
  
        modal.show();
        modalContent.innerHTML = `
          <div class="modal-body text-center p-5">
            <div class="spinner-border" role="status"></div>
          </div>`;
  
        fetch(url, {
          headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(res => res.json()) 
        .then(data => {
          modalContent.innerHTML = data.html;
        })
        .catch(err => {
          modalContent.innerHTML = `<div class="p-4 text-danger">Ошибка загрузки</div>`;
          console.error(err);
        });
      });
    });
  });
  
  

  document.addEventListener('click', function (e) {
    if (e.target.classList.contains('product-page-link')) {
      e.preventDefault();
      const page = e.target.dataset.page;
      const modalContent = document.getElementById('productModalContent');
      const productId = modalContent.getAttribute('data-product-id');
  
      fetch(`/product/${productId}/detail/?page=${page}`, {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      })
      .then(res => res.json())
      .then(data => {
        modalContent.innerHTML = data.html;
        modalContent.setAttribute('data-product-id', productId);
      })
      .catch(console.error);
    }
  });
  
  