document
  .getElementById("register-form")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    let formData = new FormData();
    formData.append("name", document.getElementById("name").value);
    formData.append("user_id", document.getElementById("user_id").value);

    let response = await fetch("/register/", {
      method: "POST",
      body: formData,
    });

    let result = await response.json();
    document.getElementById("result").innerText =
      result.message || result.detail;
  });

document
  .getElementById("auth-button")
  .addEventListener("click", async function () {
    let response = await fetch("/authenticate/", {
      method: "POST",
    });

    let result = await response.json();
    document.getElementById("result").innerText =
      result.message || result.detail;
  });
