function getCookie(name) {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith(name + '='));
  return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : null;
}

document.addEventListener('DOMContentLoaded', function () {
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');

  if (loginForm) {
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(loginForm);
      fetch(loginForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        }
      }).then(res => {
        if (res.redirected) {
          window.location.href = res.url;
        } else if (res.ok) {
          location.reload();
        } else {
          return res.text().then(html => {
            document.getElementById('loginError').innerHTML = 'Неверные данные';
          });
        }
      });
    });
  }

  if (registerForm) {
    registerForm.addEventListener('submit', function (e) {
      e.preventDefault();
      const formData = new FormData(registerForm);
      fetch(registerForm.action, {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'X-CSRFToken': getCookie('csrftoken'),
        }
      }).then(res => {
        if (res.redirected) {
          window.location.href = res.url;
        } else if (res.ok) {
          location.reload();
        } else {
          return res.text().then(html => {
            document.getElementById('registerError').innerHTML = 'Ошибка регистрации';
          });
        }
      });
    });
  }
});
