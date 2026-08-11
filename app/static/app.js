const fileInput = document.querySelector('input[name="source_file"]');
const selectedFile = document.querySelector('#selected-file');
const form = document.querySelector('form[action="/process"]');
const steps = document.querySelector('.steps');

if (fileInput && selectedFile) {
  fileInput.addEventListener('change', () => {
    selectedFile.textContent = fileInput.files[0]?.name ?? 'Aucun fichier sélectionné';
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