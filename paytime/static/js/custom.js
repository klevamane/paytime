const emailField = document.querySelector("#id_email");
const feedBackArea = document.querySelector("#invalid-feedback");

// Validate email via ajax
emailField.addEventListener("focusout", (e) =>{
    console.log("You left the email field");
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
                }
                else {
                    feedBackArea.style.display = "none";
                    emailField.classList.remove("is-invalid");
                }
            })
    }
});
