document.addEventListener("DOMContentLoaded", function () {
    const modal = new bootstrap.Modal(document.getElementById("categoryModal"));
    const form = document.getElementById("categoryForm");
    const error = document.getElementById("categoryError");
  
    document.querySelectorAll(".add-category-btn, .edit-category-btn").forEach(button => {
      button.addEventListener("click", function () {
        const isEdit = this.classList.contains("edit-category-btn");
        form.reset();
        error.classList.add("d-none");
  
        document.getElementById("categoryModalTitle").textContent = isEdit ? "Редактировать категорию" : "Добавить категорию";
        document.getElementById("categoryId").value = isEdit ? this.dataset.id : "";
        document.getElementById("categoryName").value = isEdit ? this.dataset.name : "";
  
        modal.show();
      });
    });
  
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(form);
  
      fetch("/admin/categories/save/", {
        method: "POST",
        headers: { "X-CSRFToken": formData.get("csrfmiddlewaretoken") },
        body: formData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            modal.hide();
            loadCategories();
          } else {
            error.textContent = data.error || "Ошибка при сохранении";
            error.classList.remove("d-none");
          }
        });
    });
  });
  