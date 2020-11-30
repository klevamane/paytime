const emailField = document.querySelector("#id_email");

emailField.addEventListener("keyup", (e) =>{
    console.log("You left the email field");
    const emailValue = e.target.value;
    console.log(emailValue);

    if (emailValue.length > 0) {
        fetch("/validate-user-email", {
        body: JSON.stringify({ "email": emailValue}),
        method: "POST"
    }).then(res => res.json())
            .then(data => {console.log(data)})
    }
});
