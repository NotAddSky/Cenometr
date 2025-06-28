// === CSRF для всех POST-запросов ===
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

$.ajaxSetup({
  beforeSend: function(xhr, settings) {
    if (!(/^GET|HEAD|OPTIONS|TRACE$/i.test(settings.type))) {
      xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
    }
  }
});

// === Модальное окно ===
document.addEventListener('DOMContentLoaded', function () {
  $(document).on('click', '[data-bs-target="#universalModal"]', function (e) {
    const url = $(this).data('url');

    $.get(url, function (data) {
      $('#modalBodyContent').html(data);
    });
  });

  $(document).on('submit', '#universalModal form', function (e) {
    e.preventDefault();
    const form = $(this);
    $.post(form.attr('action'), form.serialize(), function () {
      location.reload();
    }).fail(function (xhr) {
      $('#modalBodyContent').html(xhr.responseText);
    });
  });
});

// === Редактирование цен ===
$(document).on('click', '.toggle-edit-price', function () {
  const container = $(this).closest('[data-price-id]');
  const span = container.find('.price-text');
  const input = container.find('.price-input');
  const saveBtn = $(this);
  const cancelBtn = container.find('.cancel-edit-price');
  const priceId = container.data('price-id');
  const errorBox = container.next('.price-error');

  if (input.hasClass('d-none')) {
    span.addClass('d-none');
    input.removeClass('d-none').focus().select();
    cancelBtn.removeClass('d-none');
    saveBtn.text('Сохранить');
  } else {
    const rawVal = input.val().replace(',', '.');
    const newPrice = parseFloat(rawVal);

    if (isNaN(newPrice) || newPrice < 0 || newPrice > 9999999) {
      errorBox.text('Цена должна быть от 0 до 9 999 999 ₸')
        .fadeIn(200).delay(2000).fadeOut(400);
      input.addClass('is-invalid');
      setTimeout(() => input.removeClass('is-invalid'), 2000);
      return;
    }

    $.ajax({
      url: `/owner/price/${priceId}/update/`,
      method: 'POST',
      data: {
        price: newPrice,
        csrfmiddlewaretoken: getCookie('csrftoken')
      },
      success: function () {
        let formatted;
        if (Number.isInteger(newPrice)) {
          formatted = newPrice.toString().replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        } else {
          formatted = newPrice.toFixed(2).replace(/\.?0+$/, '')
            .replace(/\B(?=(\d{3})+(?!\d))/g, " ");
        }
      
        span.text(formatted + ' ₸');
        input.val(formatted);
      
        span.removeClass('d-none');
        input.addClass('d-none');
        cancelBtn.addClass('d-none');
        saveBtn.text('Редактировать');
      },
      error: function (xhr) {
        errorBox.text('Ошибка: ' + (xhr.responseJSON?.error || 'неизвестная'))
          .fadeIn(200).delay(2000).fadeOut(400);
      }
    });
  }
});



// === Кнопка "Отменить" ===
$(document).on('click', '.cancel-edit-price', function () {
  const container = $(this).closest('[data-price-id]');
  const span = container.find('.price-text');
  const input = container.find('.price-input');
  const saveBtn = container.find('.toggle-edit-price');
  const cancelBtn = $(this);

  input.val(span.text().replace(' ₸', ''));
  span.removeClass('d-none');
  input.addClass('d-none');
  cancelBtn.addClass('d-none');
  saveBtn.text('Редактировать');
});

// === Удаление товара ===
$(document).on('click', '.delete-price-btn', function () {
  const container = $(this).closest('[data-price-id]');
  const priceId = container.data('price-id');

  if (!confirm("Вы уверены, что хотите удалить этот товар?")) {
    return;
  }

  $.ajax({
    url: `/owner/price/${priceId}/delete/`,
    method: 'POST',
    success: function () {
      container.closest('tr').fadeOut(300, function () {
        $(this).remove();

        const toastEl = document.getElementById('toast-deleted');
        if (toastEl) {
          const toast = new bootstrap.Toast(toastEl);
          toast.show();
        }
      });
    },
    error: function (xhr) {
      alert('Ошибка удаления: ' + (xhr.responseJSON?.error || xhr.status));
    }
  });
});

// === Защита от букв и формат цены 0.00 ===
$(document).on('keypress', '.price-input', function (e) {
  const char = String.fromCharCode(e.which);
  const allowedChars = '0123456789.';
  const value = $(this).val();
  if (!allowedChars.includes(char)) {
    e.preventDefault();
  }
  if (char === '.' && value.includes('.')) {
    e.preventDefault();
  }
});

$(document).on('input', '.price-input', function () {
  const val = $(this).val();
  const parts = val.split('.');
  if (parts.length === 2 && parts[1].length > 2) {
    $(this).val(parts[0] + '.' + parts[1].slice(0, 2));
  }
});

// === Модалка выбора магазина ===
if (window.storeNeeded === true) {
  $.ajax({
    url: "/owner/modal/store-select/",
    method: "GET",
    headers: { "X-Requested-With": "XMLHttpRequest" },
    success: function (response) {
      if (response.html) {
        const oldModal = document.getElementById('storeSelectModal');
        if (oldModal) oldModal.remove();

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = response.html;
        document.body.appendChild(tempDiv);

        setTimeout(() => {
          const modalElement = document.getElementById('storeSelectModal');
          if (modalElement) {
            const modal = new bootstrap.Modal(modalElement);
            modal.show();

            $('#storeSelectForm').on('submit', function (e) {
              e.preventDefault();
              const storeId = $(this).find('select').val();
              if (storeId) {
                window.location.href = `${window.location.pathname}?store=${storeId}`;
              }
            });
          } else {
            console.error("Модалка storeSelectModal не найдена в DOM.");
          }
        }, 100);
      }
    },
    error: function () {
      console.error("Ошибка AJAX при получении модалки.");
    }
  });
}

// === Фильтр товаров ===
$('#filter-form').on('submit', function (e) {
  e.preventDefault();

  const $form = $(this);
  const query = $form.serialize();

  $.ajax({
    url: window.location.pathname + '?' + query,
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    success: function (response) {
      if (response.html) {
        $('#price-table-body').html(response.html);
      }
    },
    error: function () {
      console.error("Ошибка при фильтрации.");
    }
  });
});

function updateProductTable() {
  const $form = $('#filter-form');
  const query = $form.serialize();

  $('#price-table-body').addClass('loading');

  $.ajax({
    url: window.location.pathname + '?' + query,
    method: 'GET',
    headers: { 'X-Requested-With': 'XMLHttpRequest' },
    success: function (response) {
      if (response.html) {
        $('#price-table-body').html(response.html);
      }
    },
    complete: function () {
      $('#price-table-body').removeClass('loading');
    },
    error: function () {
      console.error("Ошибка при загрузке отфильтрованных данных.");
    }
  });
}

let filterTimeout = null;
$('#filter-form input[name="q"]').on('input', function () {
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(updateProductTable, 400);
});

$('#filter-form select').on('change', function () {
  updateProductTable();
});

$('#reset-filters').on('click', function () {
  const $form = $('#filter-form');
  $form[0].reset();
  updateProductTable();
});
