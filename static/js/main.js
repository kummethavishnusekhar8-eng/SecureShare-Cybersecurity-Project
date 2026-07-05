// ==============================
// PASSWORD SHOW / HIDE
// ==============================

function togglePassword() {

    const password = document.getElementById("password");
    const icon = document.getElementById("toggleIcon");

    if (!password) return;

    if (password.type === "password") {
        password.type = "text";

        if (icon) {
            icon.classList.remove("bi-eye");
            icon.classList.add("bi-eye-slash");
        }

    } else {

        password.type = "password";

        if (icon) {
            icon.classList.remove("bi-eye-slash");
            icon.classList.add("bi-eye");
        }

    }

}

// ==============================
// PASSWORD STRENGTH
// ==============================

function checkStrength() {

    const password = document.getElementById("password");

    if (!password) return;

    const value = password.value;

    const strength = document.getElementById("strength");

    const progress = document.getElementById("strengthBar");

    let score = 0;

    if (value.length >= 8) score++;
    if (/[A-Z]/.test(value)) score++;
    if (/[a-z]/.test(value)) score++;
    if (/[0-9]/.test(value)) score++;
    if (/[^A-Za-z0-9]/.test(value)) score++;

    if (!strength || !progress) return;

    switch (score) {

        case 0:
        case 1:
            strength.innerHTML = "Weak Password";
            strength.style.color = "#dc3545";
            progress.style.width = "20%";
            progress.className = "progress-bar bg-danger";
            break;

        case 2:
        case 3:
            strength.innerHTML = "Medium Password";
            strength.style.color = "#fd7e14";
            progress.style.width = "60%";
            progress.className = "progress-bar bg-warning";
            break;

        case 4:
        case 5:
            strength.innerHTML = "Strong Password";
            strength.style.color = "#198754";
            progress.style.width = "100%";
            progress.className = "progress-bar bg-success";
            break;
    }

}

// ==============================
// PASSWORD MATCH
// ==============================

function checkMatch() {

    const pass = document.getElementById("password");
    const confirm = document.getElementById("confirmPassword");

    if (!pass || !confirm) return;

    const msg = document.getElementById("matchMessage");

    if (!msg) return;

    if (confirm.value === "") {

        msg.innerHTML = "";
        return;

    }

    if (pass.value === confirm.value) {

        msg.innerHTML = "✓ Passwords Match";
        msg.style.color = "#198754";

    } else {

        msg.innerHTML = "✗ Passwords Do Not Match";
        msg.style.color = "#dc3545";

    }

}

// ==============================
// FILE SEARCH (Dashboard)
// ==============================

const search = document.getElementById("searchInput");

if (search) {

    search.addEventListener("keyup", function () {

        const value = this.value.toLowerCase();

        const cards = document.querySelectorAll(".file-card");

        cards.forEach(card => {

            const text = card.innerText.toLowerCase();

            card.style.display = text.includes(value)
                ? "block"
                : "none";

        });

    });

}

// ==============================
// DRAG & DROP UPLOAD
// ==============================

const dropArea = document.getElementById("dropArea");
const input = document.getElementById("fileInput");
const info = document.getElementById("fileInfo");

if (dropArea && input) {

    dropArea.addEventListener("dragover", e => {

        e.preventDefault();

        dropArea.classList.add("drag-active");

    });

    dropArea.addEventListener("dragleave", () => {

        dropArea.classList.remove("drag-active");

    });

    dropArea.addEventListener("drop", e => {

        e.preventDefault();

        dropArea.classList.remove("drag-active");

        input.files = e.dataTransfer.files;

        showFile();

    });

    input.addEventListener("change", showFile);

}

function showFile() {

    if (!input || !info) return;

    if (input.files.length > 0) {

        const file = input.files[0];

        info.innerHTML = `
        <div class="alert alert-success mt-3">
            <strong>Selected:</strong> ${file.name}<br>
            <strong>Size:</strong> ${(file.size / 1024).toFixed(2)} KB
        </div>
        `;

    }

}
function confirmDelete(id, filename){

    document.getElementById("deleteFileName").innerText = filename;

    document.getElementById("deleteBtn").href = "/delete/" + id;

    const modal = new bootstrap.Modal(
        document.getElementById("deleteModal")
    );

    modal.show();

}