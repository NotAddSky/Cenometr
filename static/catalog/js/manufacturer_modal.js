document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("manufacturerForm");
  const nameInput = document.getElementById("manufacturerName");
  const idInput = document.getElementById("manufacturerId");
  const modal = new bootstrap.Modal(document.getElementById("manufacturerModal"));
  const nameError = document.getElementById("nameError");

  document.querySelectorAll(".edit-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      nameInput.value = btn.dataset.name;
      idInput.value = btn.dataset.id;
      nameError.classList.add("d-none");
      document.getElementById("modalTitle").textContent = "Редактировать производителя";
    });
  });

  document.querySelector("[data-action='add']").addEventListener("click", () => {
    form.reset();
    idInput.value = "";
    nameError.classList.add("d-none");
    document.getElementById("modalTitle").textContent = "Добавить производителя";
  });

  form.addEventListener("submit", e => {
    e.preventDefault();
    const name = nameInput.value.trim();
    const id = idInput.value;

    fetch("/admin-panel/manufacturers/save/", {
      method: "POST",
      headers: {
        "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ id, name }),
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else if (data.error === "duplicate") {
        nameError.classList.remove("d-none");
      }
    });
  });

  // Удаление с подтверждением
  document.querySelectorAll(".delete-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      if (btn.classList.contains("confirming")) {
        const id = btn.dataset.id;
        fetch(`/admin-panel/manufacturers/${id}/delete/`, {
          method: "POST",
          headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
          },
        }).then(() => location.reload());
      } else {
        btn.classList.add("confirming");
        btn.textContent = "Подтвердить";
        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "Отмена";
        cancelBtn.className = "btn btn-sm btn-outline-secondary ms-2";
        cancelBtn.onclick = () => {
          btn.classList.remove("confirming");
          btn.textContent = "Удалить";
          cancelBtn.remove();
        };
        btn.parentNode.appendChild(cancelBtn);
      }
    });
  });

  // Поиск
  document.getElementById("manufacturerSearch").addEventListener("input", function () {
    const search = this.value.toLowerCase();
    document.querySelectorAll("#manufacturerTable tr").forEach(row => {
      const name = row.dataset.name;
      row.style.display = name.includes(search) ? "" : "none";
    });
  });
});
