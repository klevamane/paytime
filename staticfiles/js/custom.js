const emailField = document.querySelector(".signup-email");
const feedBackArea = document.querySelector("#invalid-feedback");
const signupButton = document.getElementById("signupsubmit");
// const verificationSentModal = document.getElementById("exampleModalCenter");


emailField.addEventListener("focusout", (e) =>{

    const emailValue = e.target.value;

    if (emailValue.length > 0) {
        fetch("/validate-user-email", {
        body: JSON.stringify({ "email": emailValue}),
        method: "POST"
    }).then(res => res.json())
            .then(data => {
                if (data.email_error) {
                    // add class to the email field
                    emailField.classList.add("is-invalid");
                    feedBackArea.innerHTML = data.email_error;
                    feedBackArea.style.display = "block";
                    // disable submit button if email has error
                    signupButton.disabled = true;
                }
                else {
                    feedBackArea.style.display = "none";
                    emailField.classList.remove("is-invalid");
                    // remove disable on submit button if email has no error
                    signupButton.removeAttribute("disabled");
                }
            });
    }
});
