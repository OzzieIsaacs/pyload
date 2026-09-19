"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const passwordInput = document.getElementById("password");
  const passwordToggle = document.getElementById("password-toggle");

  if (!passwordInput || !passwordToggle) {
    return;
  }

  const icon = passwordToggle.querySelector(".glyphicon");

  passwordToggle.addEventListener("click", () => {
    const showPassword = passwordInput.type === "password";
    const label = showPassword
      ? passwordToggle.dataset.hideLabel
      : passwordToggle.dataset.showLabel;

    passwordInput.type = showPassword ? "text" : "password";
    passwordToggle.setAttribute("aria-label", label);
    passwordToggle.setAttribute("aria-pressed", String(showPassword));
    icon.classList.toggle("glyphicon-eye-open", !showPassword);
    icon.classList.toggle("glyphicon-eye-close", showPassword);
  });
});
