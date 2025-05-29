document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.favorite-btn').forEach(button => {
      button.addEventListener('click', function () {
        const productId = this.dataset.productId;
        const isFavorite = this.dataset.isFavorite === 'true';
        const icon = this.querySelector('.favorite-icon');
  
        fetch('/favorites/toggle/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken'),
          },
          body: `product_id=${productId}`
        })
        .then(res => {
          if (res.status === 403) {
            showToast('Добавление в избранное доступно только зарегистрированным пользователям!', true);
            return Promise.reject('Not authorized');
          }
          return res.json();
        })
        .then(data => {
          if (data.success) {
            this.dataset.isFavorite = data.is_favorite ? 'true' : 'false';
            icon.classList.add('animate-favorite');
            icon.innerText = data.is_favorite ? '★' : '☆';
            setTimeout(() => icon.classList.remove('animate-favorite'), 300);
  
            const message = data.is_favorite
              ? 'Добавлено в избранное'
              : 'Удалено из избранного';
            showToast(message);
          } else {
            showToast('Ошибка при обновлении', true);
          }
        })
        .catch(error => {
          if (error !== 'Not authorized') {
            showToast('Сетевая ошибка', true);
          }
        });
      });
    });
  });


function showToast(message, isError = false) {
    const container = document.getElementById('toastStack');
  
    const toast = document.createElement('div');
    toast.className = `d-flex align-items-center gap-2 px-4 py-3 rounded shadow text-white text-center toast-fade ${isError ? 'bg-danger' : 'bg-success'}`;
    toast.style.minWidth = '240px';
  
    const icon = document.createElement('span');
    icon.textContent = isError ? '✗' : '✓';
    icon.className = 'fs-4';
  
    const text = document.createElement('span');
    text.textContent = message;
    text.className = 'flex-fill';
  
    toast.appendChild(icon);
    toast.appendChild(text);
    container.appendChild(toast);
  
    // Удаляем после завершения анимации
    setTimeout(() => {
      toast.remove();
    }, 3000);
  }
  
  
  
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
      cookie = cookie.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

  