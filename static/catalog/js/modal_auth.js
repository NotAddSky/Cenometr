$('#loginForm').on('submit', function (e) {
  e.preventDefault();

  const formData = $(this).serializeArray();
  formData.forEach(f => {
    if (f.name === 'username') f.value = f.value.toLowerCase();
  });

  $.ajax({
    url: '/accounts/login/',
    method: 'POST',
    data: $.param(formData),
    dataType: 'json', // <--- фикс: получаем JSON, а не HTML
    headers: {
      'X-CSRFToken': getCookie('csrftoken'),
      'X-Requested-With': 'XMLHttpRequest'
    },
    success: function (response) {
      if (response.location) {
        window.location.href = response.location;
      } else {
        $('#loginError').text('Ошибка входа');
      }
    },
    error: function (xhr) {
      if (xhr.status === 400 && xhr.responseJSON?.form?.errors) {
        $('#loginError').text('Неверный логин или пароль');
      } else {
        $('#loginError').text('Ошибка соединения с сервером');
      }
    }
  });
});


  
$('#registerForm').on('submit', function (e) {
  e.preventDefault();
  const formData = $(this).serialize();

  $.ajax({
    url: '/accounts/register/',
    method: 'POST',
    data: formData,
    dataType: 'html',
    success: function (response, status, xhr) {
      if ($(response).find('.errornote, .errorlist li').length) {
        const errorText = $(response).find('.errornote, .errorlist li').first().text().trim();
        $('#registerError').text(errorText || 'Ошибка регистрации');
      } else {
        const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
        modal.hide();
        location.reload();
      }
    },
    error: function () {
      $('#registerError').text('Ошибка соединения с сервером');
    }
  });
});


function onTelegramAuth(user) {
  fetch('/telegram-auth/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(user)
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      showToast('Вход выполнен через Telegram');
      setTimeout(() => location.reload(), 1000);
    } else {
      showToast('Ошибка Telegram: ' + (data.error || 'неизвестно'), true);
    }
  })
  .catch(() => showToast('Сетевая ошибка', true));
}

