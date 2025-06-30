document.addEventListener("DOMContentLoaded", function () {
    const productForm = document.getElementById("productForm");
    const productModal = new bootstrap.Modal(document.getElementById("productModal"));
    const productModalTitle = document.getElementById("productModalTitle");
    const productIdField = document.getElementById("productId");
  
    const productName = document.getElementById("productName");
    const productCategory = document.getElementById("productCategory");
    const productManufacturer = document.getElementById("productManufacturer");
    const productError = document.getElementById("productError");
  
    // Открытие модального окна
    document.querySelectorAll(".add-product-btn, .edit-product-btn").forEach(button => {
      button.addEventListener("click", function () {
        const isEdit = this.classList.contains("edit-product-btn");
        productForm.reset();
        productError.classList.add("d-none");
        productModalTitle.textContent = isEdit ? "Редактировать товар" : "Добавить товар";
        productIdField.value = "";
  
        fetch("/fetch_categories/")
          .then(res => res.json())
          .then(data => {
            productCategory.innerHTML = data.categories.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
          });
  
        fetch("/fetch_manufacturers/")
          .then(res => res.json())
          .then(data => {
            productManufacturer.innerHTML = `<option value="">—</option>` +
              data.manufacturers.map(m => `<option value="${m.id}">${m.name}</option>`).join("");
          });
  
        if (isEdit) {
          const product = JSON.parse(this.dataset.product);
          productIdField.value = product.id;
          productName.value = product.name;
          productCategory.value = product.category_id;
          productManufacturer.value = product.manufacturer_id || "";
        }
  
        productModal.show();
      });
    });
  
    // Отправка формы
    productForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(productForm);
      fetch("/admin/products/save/", {
        method: "POST",
        headers: { "X-CSRFToken": formData.get("csrfmiddlewaretoken") },
        body: formData,
      })
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            productModal.hide();
            loadProducts(); // Обновить список
          } else {
            productError.textContent = data.error || "Ошибка при сохранении";
            productError.classList.remove("d-none");
          }
        })
        .catch(() => {
          productError.textContent = "Ошибка сети";
          productError.classList.remove("d-none");
        });
    });
  });
  