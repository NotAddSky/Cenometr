document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("image");
  const preview = document.getElementById("imagePreview");

  input?.addEventListener("change", () => {
    const file = input.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = e => {
        preview.src = e.target.result;
        preview.classList.remove("d-none");
      };
      reader.readAsDataURL(file);
    } else {
      preview.classList.add("d-none");
    }
  });

  const form = document.getElementById("suggestProductForm");
  form?.addEventListener("submit", e => {
    e.preventDefault();

    const formData = new FormData(form);

    fetch("/admin-panel/suggest-product/", {
      method: "POST",
      headers: {
        "X-CSRFToken": form.querySelector("[name=csrfmiddlewaretoken]").value,
      },
      body: formData,
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        form.reset();
        preview.classList.add("d-none");
        bootstrap.Modal.getInstance(document.getElementById("suggestProductModal")).hide();
        alert("Предложение отправлено!");
      } else {
        alert("Ошибка: " + (data.error || "Не удалось отправить предложение"));
      }
    })
    .catch(() => alert("Ошибка сети"));
  });
});
