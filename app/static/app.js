const fileInput = document.querySelector('input[name="source_file"]');
const selectedFile = document.querySelector('#selected-file');
const form = document.querySelector('form[action="/process"]');
const steps = document.querySelector('.steps');

if (fileInput && selectedFile) {
  fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    if (!files || files.length === 0) {
      selectedFile.textContent = 'Aucun fichier sélectionné';
      return;
    }

    selectedFile.textContent = files.length === 1
      ? files[0].name
      : `${files.length} fichiers sélectionnés`;
  });
}

if (form && steps) {
  form.addEventListener('submit', () => {
    steps.hidden = false;
    [...steps.children].forEach((step, index) => {
      window.setTimeout(() => step.classList.add('active'), index * 250);
    });
  });
}