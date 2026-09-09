// QuaNet Vision - Satellite Studio Scripts
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('satFileInput');
    const previewImg = document.getElementById('satPreviewImg');
    const uploadPrompt = document.getElementById('uploadPrompt');
    const sampleCards = document.querySelectorAll('.sample-sat-card');
    const sampleInput = document.getElementById('selectedSampleInput');

    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = (event) => {
                    if (previewImg) {
                        previewImg.src = event.target.result;
                        previewImg.style.display = 'block';
                    }
                    if (uploadPrompt) uploadPrompt.style.display = 'none';
                };
                reader.readAsDataURL(file);
                if (sampleInput) sampleInput.value = '';
                sampleCards.forEach(c => c.classList.remove('selected-sample'));
            }
        });
    }

    sampleCards.forEach(card => {
        card.addEventListener('click', () => {
            const filename = card.getAttribute('data-filename');
            const category = card.getAttribute('data-category').toLowerCase();
            const imgUrl = `/dataset-img/${category}/${filename}`;
            
            if (sampleInput) sampleInput.value = filename;
            if (fileInput) fileInput.value = '';
            
            if (previewImg) {
                previewImg.src = imgUrl;
                previewImg.style.display = 'block';
            }
            if (uploadPrompt) uploadPrompt.style.display = 'none';

            sampleCards.forEach(c => c.classList.remove('selected-sample'));
            card.classList.add('selected-sample');
        });
    });
});
