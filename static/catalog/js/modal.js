document.addEventListener("DOMContentLoaded", function () {
  const modalBody = document.getElementById("modalBodyContent");

  // При открытии модалки — загружаем содержимое по data-url
  if ($('#universalModal').length) { 
    $('#universalModal').on('show.bs.modal', function (event) {
    const trigger = event.relatedTarget;
    const url = trigger.getAttribute("data-url");

    if (url) {
      fetch(url)
        .then(response => response.text())
        .then(html => {
          modalBody.innerHTML = html;

          const form = modalBody.querySelector("form");
          if (form) {
            form.addEventListener("submit", function (e) {
              e.preventDefault();
              const formData = new FormData(form);
              fetch(form.action, {
                method: "POST",
                body: formData,
                headers: { "X-Requested-With": "XMLHttpRequest" }
              }).then(res => {
                if (res.status === 204) {
                  window.location.reload(); // или обновить часть страницы
                } else {
                  return res.text().then(html => {
                    modalBody.innerHTML = html; // показать ошибки
                  });
                }
              });
            });
          }
        });
    }
  });
}});

document.addEventListener('DOMContentLoaded', function () {
  document.body.addEventListener('click', function (e) {
    if (e.target.classList.contains('report-btn')) {
      const productId = e.target.dataset.productId;
      const storeId = e.target.dataset.storeId;
      document.getElementById('complaintProductId').value = productId;
      document.getElementById('complaintStoreId').value = storeId;
      const complaintModal = new bootstrap.Modal(document.getElementById('complaintModal'));
      complaintModal.show();
    }
  });

  document.getElementById('complaintForm').addEventListener('submit', function (e) {
    e.preventDefault();

    const form = e.target;
    const formData = new FormData(form);
    const url = form.dataset.url;
    fetch(url, {
      method: 'POST',
      headers: {
        'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData
    })  
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const modal = bootstrap.Modal.getInstance(document.getElementById('complaintModal'));
        modal.hide();
        showToast('Жалоба отправлена. Спасибо!');
      } else {
        showToast('Ошибка: ' + data.error, true);
      }
    })
    .catch(() => {
      showToast('Сетевая ошибка', true);
    });
  });
});


function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
  headers: { "X-CSRFToken": csrftoken }
});

