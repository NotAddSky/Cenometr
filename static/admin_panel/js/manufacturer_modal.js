document.addEventListener("DOMContentLoaded", function () {
    const modal = new bootstrap.Modal(document.getElementById("manufacturerModal"));
    const form = document.getElementById("manufacturerForm");
    const error = document.getElementById("manufacturerError");
  
    document.querySelectorAll(".add-manufacturer-btn, .edit-manufacturer-btn").forEach(button => {
      button.addEventListener("click", function () {
        const isEdit = this.classList.contains("edit-manufacturer-btn");
        form.reset();
        error.classList.add("d-none");
  
        document.getElementById("manufacturerModalTitle").textContent = isEdit ? "Редактировать производителя" : "Добавить производителя";
        document.getElementById("manufacturerId").value = isEdit ? this.dataset.id : "";
        document.getElementById("manufacturerName").value = isEdit ? this.dataset.name : "";
  
        modal.show();
      });
    });
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(form);
  
      fetch("/admin/manufacturers/save/", {
        method: "POST",
        headers: { "X-CSRFToken": formData.get("csrfmiddlewaretoken") },
        body: formData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            modal.hide();
            loadManufacturers();
          } else {
            error.textContent = data.error || "Ошибка при сохранении";
            error.classList.remove("d-none");
          }
        });
    });
  });
  