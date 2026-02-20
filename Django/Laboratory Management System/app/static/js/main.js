// Main JS for Lab Secure

// Toggle Password Visibility
function togglePassword(fieldId, iconId) {
    const field = document.getElementById(fieldId);
    const icon = document.getElementById(iconId);
    if (field && icon) {
        if (field.type === "password") {
            field.type = "text";
            icon.classList.replace("fa-eye", "fa-eye-slash");
        } else {
            field.type = "password";
            icon.classList.replace("fa-eye-slash", "fa-eye");
        }
    }
}

// Client-side validation for Bootstrap
(function () {
    'use strict'
    const forms = document.querySelectorAll('.needs-validation')
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault()
                event.stopPropagation()
            }
            form.classList.add('was-validated')
        }, false)
    })
})()
