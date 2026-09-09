// QuaNet Vision - Prediction Form & AJAX Handler
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('predictionForm');
    const submitBtn = document.getElementById('predictBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const resultContainer = document.getElementById('resultContainer');

    // Preset button handlers
    const presetBtns = document.querySelectorAll('.preset-btn');
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const data = JSON.parse(btn.getAttribute('data-preset'));
            document.getElementById('inputPH').value = data.ph;
            document.getElementById('inputTemp').value = data.temperature;
            document.getElementById('inputTurbidity').value = data.turbidity;
            document.getElementById('inputDO').value = data.dissolved_oxygen;
            document.getElementById('inputTDS').value = data.tds;
            document.getElementById('inputConductivity').value = data.conductivity;
            
            // Highlight button
            presetBtns.forEach(b => b.classList.remove('active-preset'));
            btn.classList.add('active-preset');
        });
    });

    // Satellite image preview
    const imageInput = document.getElementById('satelliteImageInput');
    const imagePreview = document.getElementById('imagePreview');
    if (imageInput && imagePreview) {
        imageInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    imagePreview.src = event.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        });
    }

    if (form) {
        form.addEventListener('submit', () => {
            if (submitBtn && btnText && btnSpinner) {
                submitBtn.disabled = true;
                btnText.textContent = 'Analyzing water-quality data...';
                btnSpinner.style.display = 'inline-block';
            }
        });
    }
});
