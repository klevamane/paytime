const emailField = document.querySelector("#id_email");
const feedBackArea = document.querySelector("#invalid-feedback");

emailField.addEventListener("focusout", (e) =>{
    console.log("You left the email field");
    const emailValue = e.target.value;
    console.log(emailValue);

    if (emailValue.length > 0) {
        fetch("/validate-user-email", {
        body: JSON.stringify({ "email": emailValue}),
        method: "POST"
    }).then(res => res.json())
            .then(data => {
                console.log("THE DATDA", data);
                if (data.email_error) {
                    emailField.classList.add("is-invalid");
                    feedBackArea.innerHTML = data.email_error;
                    feedBackArea.style.display = "block";
                    console.log("EFFICIENT", data.email_error);
                }
                else {
                    feedBackArea.style.display = "none";
                    emailField.classList.remove("is-invalid")
                }
            })
    }
});
