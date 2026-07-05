import os
import uuid

from flask import (
    render_template,
    request,
    redirect,
    send_file,
    flash,
    abort
)

from datetime import datetime, timedelta

from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.utils import secure_filename

from app import app, bcrypt
from models import db, User, File
from encryption import encrypt_file, decrypt_file


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():
    return render_template("home.html")


# ==========================================================
# REGISTER
# ==========================================================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        # Check username
        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "danger"
            )

            return redirect("/register")

        # Check email
        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "Email already registered.",
                "danger"
            )

            return redirect("/register")

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(
            username=username,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        flash(
            "Registration successful. Please login.",
            "success"
        )

        return redirect("/login")

    return render_template("register.html")


# ==========================================================
# LOGIN
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        user = User.query.filter_by(
            username=username
        ).first()

        if user and bcrypt.check_password_hash(
            user.password,
            password
        ):

            login_user(user)

            flash(
                f"Welcome back, {user.username}!",
                "success"
            )

            return redirect("/dashboard")

        flash(
            "Invalid username or password.",
            "danger"
        )

        return redirect("/login")

    return render_template("login.html")


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/dashboard")
@login_required
def dashboard():

    files = File.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "dashboard.html",
        files=files
    )


# ==========================================================
# MY FILES
# ==========================================================

@app.route("/files")
@login_required
def files():

    files = File.query.filter_by(
        user_id=current_user.id
    ).all()

    return render_template(
        "files.html",
        files=files
    )


# ==========================================================
# UPLOAD FILE
# ==========================================================

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():

    if request.method == "POST":

        if "file" not in request.files:

            flash(
                "Please choose a file.",
                "warning"
            )

            return redirect("/upload")

        uploaded_file = request.files["file"]

        if uploaded_file.filename == "":

            flash(
                "Please choose a file.",
                "warning"
            )

            return redirect("/upload")

        filename = secure_filename(
            uploaded_file.filename
        )

        upload_folder = "uploads"
        encrypted_folder = "encrypted_files"

        os.makedirs(
            upload_folder,
            exist_ok=True
        )

        os.makedirs(
            encrypted_folder,
            exist_ok=True
        )

        upload_path = os.path.join(
            upload_folder,
            filename
        )

        encrypted_filename = filename + ".enc"

        encrypted_path = os.path.join(
            encrypted_folder,
            encrypted_filename
        )

        uploaded_file.save(upload_path)

        encrypt_file(
            upload_path,
            encrypted_path
        )

        filesize = round(
            os.path.getsize(upload_path) / 1024,
            2
        )

        os.remove(upload_path)

        file = File(
            filename=filename,
            encrypted_filename=encrypted_filename,
            filesize=filesize,
            user_id=current_user.id
        )

        db.session.add(file)
        db.session.commit()

        flash(
            "File uploaded and encrypted successfully.",
            "success"
        )

        return redirect("/files")

    return render_template("upload.html")
# ==========================================================
# DOWNLOAD
# ==========================================================

@app.route("/download/<int:file_id>")
@login_required
def download(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:

        flash(
            "Unauthorized access.",
            "danger"
        )

        return redirect("/files")

    encrypted_path = os.path.join(
        "encrypted_files",
        file.encrypted_filename
    )

    decrypted_path = os.path.join(
        "uploads",
        file.filename
    )

    decrypt_file(
        encrypted_path,
        decrypted_path
    )

    file.downloads += 1

    db.session.commit()

    return send_file(
        decrypted_path,
        as_attachment=True
    )
# ==========================================================
# PREVIEW FILE
# ==========================================================

from flask import send_from_directory

@app.route("/preview/<int:file_id>")
@login_required
def preview(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:

        flash(
            "Unauthorized access.",
            "danger"
        )

        return redirect("/files")

    encrypted_path = os.path.join(
        "encrypted_files",
        file.encrypted_filename
    )

    upload_folder = "uploads"

    decrypted_path = os.path.join(
        upload_folder,
        file.filename
    )

    decrypt_file(
        encrypted_path,
        decrypted_path
    )

    ext = file.filename.split(".")[-1].lower()

    if ext in [
        "png",
        "jpg",
        "jpeg",
        "gif",
        "webp",
        "pdf",
        "txt"
    ]:

        return render_template(
            "preview.html",
            file=file,
            extension=ext
        )

    flash(
        "Preview not supported. File downloaded instead.",
        "warning"
    )

    return send_file(
        decrypted_path,
        as_attachment=True
    )


# ==========================================================
# SHARE FILE
# ==========================================================



@app.route("/share/<int:file_id>", methods=["GET", "POST"])
@login_required
def share(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:

        flash("Unauthorized access.", "danger")

        return redirect("/files")

    days = request.args.get("days", type=int, default=7)

    password = request.args.get("password", "").strip()

    if not file.share_token:
        file.share_token = str(uuid.uuid4())

    file.shared = True

    if days == 0:
        file.expiry_date = None
    else:
        file.expiry_date = datetime.utcnow() + timedelta(days=days)

    # Store password (hashed)
    if password:
        file.share_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")
    else:
        file.share_password = None

    db.session.commit()

    flash(
        "Secure share link created successfully.",
        "success"
    )

    return redirect("/files")



# ==========================================================
# PUBLIC SHARE
# ==========================================================

@app.route("/shared/<token>", methods=["GET", "POST"])
def shared(token):

    file = File.query.filter_by(
        share_token=token
    ).first_or_404()

    # Check expiry
    if file.expiry_date and datetime.utcnow() > file.expiry_date:
        abort(410)

    # Password protection
    if file.share_password:

        if request.method == "POST":

            password = request.form["password"]

            if bcrypt.check_password_hash(
                file.share_password,
                password
            ):

                encrypted_path = os.path.join(
                    "encrypted_files",
                    file.encrypted_filename
                )

                decrypted_path = os.path.join(
                    "uploads",
                    file.filename
                )

                decrypt_file(
                    encrypted_path,
                    decrypted_path
                )

                file.downloads += 1

                db.session.commit()

                return send_file(
                    decrypted_path,
                    as_attachment=True
                )

            flash(
                "Incorrect password.",
                "danger"
            )

        return render_template(
            "shared_download.html",
            file=file
        )

    encrypted_path = os.path.join(
        "encrypted_files",
        file.encrypted_filename
    )

    decrypted_path = os.path.join(
        "uploads",
        file.filename
    )

    decrypt_file(
        encrypted_path,
        decrypted_path
    )

    file.downloads += 1

    db.session.commit()

    return send_file(
        decrypted_path,
        as_attachment=True
    )

# ==========================================================
# FAVORITE
# ==========================================================

@app.route("/favorite/<int:file_id>")
@login_required
def favorite(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:

        flash(
            "Unauthorized access.",
            "danger"
        )

        return redirect("/files")

    file.favorite = not file.favorite

    db.session.commit()

    if file.favorite:

        flash(
            "Added to favorites.",
            "success"
        )

    else:

        flash(
            "Removed from favorites.",
            "warning"
        )

    return redirect("/files")


# ==========================================================
# DELETE
# ==========================================================

@app.route("/delete/<int:file_id>")
@login_required
def delete(file_id):

    file = File.query.get_or_404(file_id)

    if file.user_id != current_user.id:

        flash(
            "Unauthorized access.",
            "danger"
        )

        return redirect("/files")

    encrypted_path = os.path.join(
        "encrypted_files",
        file.encrypted_filename
    )

    if os.path.exists(encrypted_path):

        os.remove(encrypted_path)

    db.session.delete(file)

    db.session.commit()

    flash(
        "File deleted successfully.",
        "danger"
    )

    return redirect("/files")


# ==========================================================
# PROFILE
# ==========================================================

@app.route("/profile")
@login_required
def profile():

    return render_template(
        "profile.html"
    )


# ==========================================================
# SETTINGS
# ==========================================================

@app.route("/settings")
@login_required
def settings():

    return render_template(
        "settings.html"
    )


# ==========================================================
# ADMIN PANEL
# ==========================================================

@app.route("/admin")
@login_required
def admin():

    if not current_user.is_admin:

        flash(
            "Access denied.",
            "danger"
        )

        return redirect("/dashboard")

    users = User.query.all()

    files = File.query.all()

    return render_template(
        "admin.html",
        users=users,
        files=files
    )


# ==========================================================
# LOGOUT
# ==========================================================

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect("/login")