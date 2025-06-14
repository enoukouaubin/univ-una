document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    if (form) {
        form.addEventListener('submit', function(e) {
            const dateInput = form.querySelector('input[type="date"]');
            if (new Date(dateInput.value) < new Date()) {
                e.preventDefault();
                alert('Veuillez sélectionner une date future.');
            }
        });
    }
});