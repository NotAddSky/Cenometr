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
      location.reload();
    } else {
      alert("Ошибка авторизации через Telegram");
    }
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const testBtn = document.getElementById('testTelegramBtn');
  if (testBtn) {
    testBtn.addEventListener('click', () => {
      const testUser = {
        id: 123456789,
        username: 'test_user',
        first_name: 'Test',
        last_name: 'User',
        auth_date: Math.floor(Date.now() / 1000),
        hash: 'dummy'  // На этапе теста пока игнорируем проверку подписи
      };

      fetch('/telegram-auth/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify(testUser)
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          showToast('Успешный вход как Telegram-пользователь');
          setTimeout(() => location.reload(), 1000);
        } else {
          showToast('Ошибка: ' + (data.error || 'неизвестно'), true);
        }
      })
      .catch(() => showToast('Сетевая ошибка', true));
    });
  }
});

