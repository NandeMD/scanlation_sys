from flask import Blueprint, request, render_template, flash, redirect, url_for
from .models import User
from . import db
from re import search as re_search
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user

auth = Blueprint("auth", __name__)
EMAIL_REGEX = r"^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("views.home"))

    if request.method == "POST":
        username = request.form.get("login-username")
        password = request.form.get("login-pwd")

        user = User.query.filter_by(username=username).first()

        if user:
            if check_password_hash(user.password, password):
                flash("Login succcessful!", category="success")
                login_user(user)
                return redirect(url_for("series_views.home"))
            else:
                flash("Incorrect password!", category="error")
        else:
            flash("Can't find user.")

    return render_template("login.html", user=current_user)


# noinspection PyArgumentList
@auth.route("/create-user", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        email = request.form.get("create-user-email")
        username = request.form.get("create-user-username")
        pwd1 = request.form.get("create-user-pwd")
        pwd2 = request.form.get("create-user-pwd-cnf")
        role = request.form.get("create-user-role")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash('E-Mail already taken.ç', category='error')
        elif username_exists:
            flash('Username already taken.', category='error')
        elif not email or not username or not pwd1 or not pwd2:
            flash("Please fill all inputs.", category='error')
        elif pwd1 != pwd2:
            flash("Passwords do not match.", category='error')
        elif len(username) < 2:
            flash('Username must contain at least 2 characters.', category='error')
        elif len(pwd1) < 6:
            flash('Password must contain at least 6 characters.', category='error')
        elif len(email) < 6:
            flash("E-Mail is too short.", category='error')
        elif not re_search(EMAIL_REGEX, email):
            flash("Invalid E-Mail address.", category='error')
        else:
            new_user = User(email=email,
                            username=username,
                            password=generate_password_hash(pwd1, method="sha256"),
                            role=role)
            db.session.add(new_user)
            db.session.commit()
            flash("User created successfully.")

        return redirect(url_for("auth.create_user"))

    return render_template("create-user.html", user=current_user)


@auth.route("/logout")
def logout():
    flash("Logged Out!", category="success")
    logout_user()
    return redirect(url_for("auth.login"))


@auth.route("/account-settings", methods=["GET", "POST"])
def account_settings():
    if request.method == "POST":
        email = request.form.get("settings-user-email")
        username = request.form.get("settings-user-username")
        pwd1 = request.form.get("settings-user-pwd")
        pwd2 = request.form.get("settings-user-pwd-cnf")
        pwd_old = request.form.get("settings-user-pwd-old")

        if not email and not username and (not pwd1 or not pwd2):
            flash("No changes were entered to be updated.", category="info")
        elif not pwd_old:
            flash("The current password was not entered.", category="error")
        elif email and not re_search(EMAIL_REGEX, email):
            flash("Invalid E-Mail address.", category='error')
        elif username and len(username) < 2:
            flash('Username must contain at least 2 characters.', category='error')
        elif pwd1 and len(pwd1) < 6:
            flash('Password must contain at least 6 characters.', category='error')
        elif (pwd1 or pwd2) and (pwd1 != pwd2):
            flash("New passwords do not match!", category="error")
        elif email and len(email) < 6:
            flash("E-Mail is too short.", category='error')
        else:
            email_exists = User.query.filter_by(email=email).first()
            username_exists = User.query.filter_by(username=username).first()

            if email_exists:
                flash('E-Mail already in use.', category='error')
            elif username_exists:
                flash('Username already in use.', category='error')
            else:
                if not check_password_hash(current_user.password, pwd_old):
                    flash("Current password is wrong!", category="error")
                else:
                    user = User.query.filter_by(id=current_user.id).first()
                    user.email = email if email else user.email
                    user.username = username if username else user.username
                    user.password = generate_password_hash(pwd1, method="sha256") if pwd1 else user.password
                    db.session.commit()

                    flash("Account successfully updated.", category="success")

        return redirect(url_for("auth.account_settings"))

    return render_template("account-settings.html", user=current_user)


@auth.route("/delete-user", methods=["GET", "POST"])
def delete_user():
    if request.method == "POST":

        aydi = request.form.get("delete-id")
        id_exists = User.query.filter_by(id=aydi).first()

        if not id_exists:
            flash("Such an ID could not be found. Please refer to the user list below.", category="error")
        elif current_user.id == id_exists.id:
            flash("You cannot delete yourself!", category="error")
        elif current_user.role == "normal" or (current_user.role == "admin" and id_exists.role == "admin") or (current_user.role == "admin" and id_exists.role == "super") or (current_user.role == "super" and id_exists.role == "super"):
            flash(f"You do not have the permission to delete this user.\t\t[{current_user.role}] -> [{id_exists.role}]", category="error")
        else:
            deleted_name = id_exists.username
            db.session.delete(id_exists)
            db.session.commit()
            flash(f"The user {deleted_name} has been successfully deleted.", category="success")

    all_users = User.query.all()
    return render_template("delete-user.html", user=current_user, all_users=all_users)
