function showForm(formId) {
  document.querySelectorAll(".form-box").forEach((form) => {
    return form.classList.remove("active");
  });
  document.getElementById(formId).classList.add("active");
}

document.addEventListener("DOMContentLoaded", () => {
  showForm("login-form");
});
