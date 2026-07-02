// Client-side validation for login/register forms.
// Server-side validation in routes/auth_routes.py is the source of truth;
// this just gives the user instant feedback before submitting.

document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");

    if (registerForm) {
        registerForm.addEventListener("submit", (e) => {
            const password = document.getElementById("password").value;
            const confirmPassword = document.getElementById("confirm_password").value;

            if (password !== confirmPassword) {
                e.preventDefault();
                alert("Passwords do not match.");
                return;
            }

            const hasLetter = /[a-zA-Z]/.test(password);
            const hasDigit = /[0-9]/.test(password);
            if (password.length < 8 || !hasLetter || !hasDigit) {
                e.preventDefault();
                alert("Password must be at least 8 characters and include a letter and a number.");
            }
        });
    }
});
