document.addEventListener('DOMContentLoaded', function () {
  const panel = document.getElementById('todoPanel');
  const toggleBtn = document.getElementById('todoToggleBtn');
  const form = document.getElementById('todoForm');
  const list = document.getElementById('todoList');
  const filter = document.getElementById('statusFilter');
  const resizeHandle = document.querySelector('.resize-handle-start');

  // Проверка: если элементы отсутствуют (неавторизованный пользователь), выходим
  if (!panel || !toggleBtn || !form || !list || !filter || !resizeHandle) {
    return;
  }

  let isResizing = false;

  toggleBtn.addEventListener('click', () => {
    panel.classList.toggle('d-none');
  });

  function loadTasks() {
    fetch('/api/todo/')
      .then(res => res.json())
      .then(data => {
        renderTasks(data.tasks);
      });
  }

  form.addEventListener('submit', e => {
    e.preventDefault();
    const title = form.title.value.trim();
    if (!title) return;
    fetch('/api/todo/create/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ title })
    }).then(() => {
      form.title.value = '';
      loadTasks();
    });
  });

  function renderTasks(tasks) {
    const selected = filter.value;
    list.innerHTML = '';

    tasks.forEach(task => {
      if (selected !== 'all' && task.status !== selected) return;

      const li = document.createElement('li');
      li.className = `list-group-item position-relative border-start border-4 mb-1 fade-in ${statusColor(task.status)}`;
      li.dataset.id = task.id;

      li.innerHTML = `
        <button class="btn btn-sm btn-outline-danger btn-close position-absolute top-0 end-0 m-1 delete-task-btn" title="Удалить" data-id="${task.id}"></button>
        <div class="todo-item-text pe-4">${task.title}</div>
        <select class="form-select form-select-sm mt-2 todo-status-select" data-id="${task.id}">
          <option value="new" ${task.status === 'new' ? 'selected' : ''}>🕒 Новая</option>
          <option value="in_progress" ${task.status === 'in_progress' ? 'selected' : ''}>⚙ В работе</option>
          <option value="done" ${task.status === 'done' ? 'selected' : ''}>✅ Готово</option>
          <option value="cancelled" ${task.status === 'cancelled' ? 'selected' : ''}>❌ Отменено</option>
        </select>
      `;
      list.appendChild(li);
    });
  }

  function statusColor(status) {
    switch (status) {
      case 'new': return 'border-secondary';
      case 'in_progress': return 'border-warning';
      case 'done': return 'border-success';
      case 'cancelled': return 'border-danger';
      default: return '';
    }
  }

  list.addEventListener('click', function (e) {
    if (e.target.classList.contains('delete-task-btn')) {
      const id = e.target.dataset.id;
      const item = e.target.closest('li');
      item.classList.add('fade-out');

      fetch(`/api/todo/${id}/delete/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCookie('csrftoken'),
        }
      }).then(() => {
        setTimeout(() => {
          item.remove();
        }, 300);
      });
    }
  });

  list.addEventListener('change', function (e) {
    if (e.target.classList.contains('todo-status-select')) {
      const id = e.target.dataset.id;
      const status = e.target.value;

      fetch(`/api/todo/${id}/update/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken'),
        },
        body: JSON.stringify({ status })
      }).then(() => loadTasks());
    }
  });

  filter.addEventListener('change', loadTasks);

  Sortable.create(list, {
    animation: 150,
    handle: '.todo-item-text',
  });

  resizeHandle.addEventListener('mousedown', e => {
    isResizing = true;
    document.body.style.cursor = 'ew-resize';
  });

  window.addEventListener('mousemove', e => {
    if (!isResizing) return;
    panel.style.width = `${Math.max(250, e.clientX - panel.offsetLeft)}px`;
  });

  window.addEventListener('mouseup', () => {
    isResizing = false;
    document.body.style.cursor = 'default';
  });

  loadTasks();
});

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
