const usernameField = document.querySelector("#usernameField");
const feedBackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const usernameSuccessOutput = document.querySelector(".usernameSuccessOutput")
const emailSuccessOutput = document.querySelector(".emailSuccessOutput")
const showPasswordToggle = document.querySelector(".showPasswordToggle")
const passwordField = document.querySelector("#passwordField")
const submitBtn = document.querySelector(".submit-btn")


const handleToggleInput = (e) => {

    if (showPasswordToggle.textContent === 'SHOW') {
        showPasswordToggle.textContent = "HIDE";

        passwordField.setAttribute("type", "text");
    } else {
        showPasswordToggle.textContent = "SHOW";

        passwordField.setAttribute("type", "password");
    }
};

showPasswordToggle.addEventListener('click', handleToggleInput);

emailField.addEventListener("keyup", (e) => {
    e.preventDefault();
    const emailVal = e.target.value;
    emailSuccessOutput.style.display = "block"
    emailSuccessOutput.textContent = `Checking ${emailVal}`


    // Clearing errors when the user is typing
    emailField.classList.remove("is-invalid");
    emailFeedBackArea.style.display = 'none';

    if (emailVal.length > 0) {
        // API CALL
        fetch('/users/validate-email/', {
            body: JSON.stringify({ 'email': emailVal }),
            method: "POST",
            headers: { 'Content-Type': 'application/json' } // Corrected the header name

        }).then(res => res.json()).then(data => {
            console.log("data", data);
            emailSuccessOutput.style.display = "none"
            if (data.email_error) {
                submitBtn.setAttribute('disabled', 'disabled');
                submitBtn.disabled = true;
                emailField.classList.add("is-invalid");
                emailFeedBackArea.style.display = 'block';
                emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
            } else {
                submitBtn.removeAttribute("disabled");
            }
        });
    }

});

usernameField.addEventListener("keyup", (e) => {
    const usernameVal = e.target.value;
    usernameSuccessOutput.style.display = "block"
    usernameSuccessOutput.textContent = `Checking ${usernameVal}`

    // Clearing errors when the user is typing
    usernameField.classList.remove("is-invalid");
    feedBackArea.style.display = 'none';

    if (usernameVal.length > 0) {
        // API CALL
        fetch('/users/validate-username/', {
            body: JSON.stringify({ 'username': usernameVal }),
            method: "POST",
            headers: { 'Content-Type': 'application/json' } // Corrected the header name

        }).then(res => res.json()).then(data => {
            console.log("data", data);
            usernameSuccessOutput.style.display = "none"
            if (data.username_error) {
                submitBtn.setAttribute('disabled', 'disabled');
                submitBtn.disabled = true;
                usernameField.classList.add("is-invalid");
                feedBackArea.style.display = 'block';
                feedBackArea.innerHTML = `<p>${data.username_error}</p>`; // Use backticks (`) for string interpolation
            } else {
                submitBtn.removeAttribute('disabled');
            }
        });
    }
});