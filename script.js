const pwdInput = document.getElementById("pwd");
const bar = document.getElementById("bar");
const scoreText = document.getElementById("scoreText");
const labelText = document.getElementById("labelText");
const suggestionsList = document.getElementById("suggestions");
const mainResult = document.getElementById("mainResult");
const copyBtn = document.getElementById("copyBtn");
const genBtn = document.getElementById("genBtn");
const togglePwd = document.getElementById("togglePwd");

// check password function
function checkPassword(password) {
  if (!password) {
    bar.style.width = "0%";
    scoreText.textContent = "Score: —";
    labelText.textContent = "Strength: —";
    mainResult.textContent = "Start typing to check...";
    suggestionsList.innerHTML = "";
    return;
  }

  const result = zxcvbn(password);

  // bar
  const colors = ["var(--weak)", "var(--weak)", "var(--fair)", "var(--strong)", "var(--very-strong)"];
  bar.style.width = ((result.score + 1) / 5) * 100 + "%";
  bar.style.background = colors[result.score];

  // score & label
  scoreText.textContent = "Score: " + result.score + " / 4";
  const labels = ["Very Weak", "Weak", "Fair", "Strong", "Very Strong"];
  labelText.textContent = "Strength: " + labels[result.score];

  // main output
  mainResult.textContent = `It would take ${result.crack_times_display.offline_slow_hashing_1e4_per_second} to crack your password.`;

  // suggestions
  suggestionsList.innerHTML = "";
  if (result.feedback.suggestions.length > 0) {
    result.feedback.suggestions.forEach(s => {
      const li = document.createElement("li");
      li.textContent = s;
      suggestionsList.appendChild(li);
    });
  } else {
    const li = document.createElement("li");
    li.textContent = "Your password looks strong!";
    suggestionsList.appendChild(li);
  }
}

// live typing check
pwdInput.addEventListener("input", () => {
  checkPassword(pwdInput.value);
});

// copy password
copyBtn.addEventListener("click", () => {
  if (pwdInput.value) {
    navigator.clipboard.writeText(pwdInput.value);
    alert("Password copied to clipboard!");
  } else {
    alert("Enter a password first!");
  }
});

// generate strong password
genBtn.addEventListener("click", () => {
  const chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+{}[]<>?";
  let newPass = "";
  for (let i = 0; i < 16; i++) {
    newPass += chars[Math.floor(Math.random() * chars.length)];
  }
  pwdInput.value = newPass;
  checkPassword(newPass);
});

// toggle show/hide password
togglePwd.addEventListener("click", () => {
  if (pwdInput.type === "password") {
    pwdInput.type = "text";
    togglePwd.textContent = "🙈"; // change icon
  } else {
    pwdInput.type = "password";
    togglePwd.textContent = "👁️";
  }
});
