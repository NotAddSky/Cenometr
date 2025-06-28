let cropper;

document.getElementById('avatarInput').addEventListener('change', function () {
  const file = this.files[0];
  if (!file) return;

  const img = document.getElementById('avatarPreview');
  img.src = URL.createObjectURL(file);
  img.style.display = 'block';
  document.getElementById('avatarPreviewContainer').style.display = 'block';

  if (cropper) cropper.destroy();
  cropper = new Cropper(img, {
    aspectRatio: 1,
    viewMode: 1,
    minContainerWidth: 300,
    minContainerHeight: 300,
    preview: '.preview'
  });
});

document.getElementById('saveAvatarBtn').addEventListener('click', function () {
  if (!cropper) return;

  const canvas = cropper.getCroppedCanvas({
    width: 300,
    height: 300,
    imageSmoothingEnabled: true,
    imageSmoothingQuality: 'high',
  }); 

  canvas.toBlob(blob => {
    const formData = new FormData();
    formData.append('avatar', blob, 'avatar.webp');

    fetch('/profile/upload-avatar/', {
      method: 'POST',
      headers: { 'X-CSRFToken': getCookie('csrftoken') },
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        location.reload();
      } else {
        document.getElementById('avatarError').textContent = data.error || 'Ошибка загрузки';
      }
    });
  }, 'image/webp', 1);
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  return parts.length === 2 ? parts.pop().split(';').shift() : '';
}
