from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from requests import get as rget, post as rpost, ConnectionError as rConnErr
from json import loads
from config import get_api_ip


series_views = Blueprint("series_views", __name__)

base_api_ip = get_api_ip()


@series_views.route('/')
@login_required
def home():
    if not session.get("qmode"):
        session["qmode"] = "desc"

    param = request.args.get("param")
    mode = request.args.get("mode")

    rseries = None

    if not param or not mode:
        with rget(f"http://{base_api_ip}/series/get/") as response:
            rseries = loads(response.text)["series"]
    else:
        with rget(f"http://{base_api_ip}/series/get/order-by/?param={param}&mode={mode}") as response:
            rseries = loads(response.text)["results"]
            if mode == "asc":
                session["qmode"] = "desc"
            else:
                session["qmode"] = "asc"

    return render_template("home.html", user=current_user, mangas=rseries, qmode=session["qmode"])


@series_views.route("/manga-personnel")
@login_required
def manga_personnel():
    with rget(f"http://{base_api_ip}/series/get/") as response:
        rseries = loads(response.text)["series"]

    return render_template("manga-personnel-page.html", user=current_user, mangas=rseries)


@series_views.route("/create-manga", methods=["POST", "GET"])
@login_required
def create_manga():
    if request.method == "POST":
        name = request.form.get("create-manga-serie-name")
        img_url = request.form.get("create-manga-img-url")
        source_url = request.form.get("create-manga-source")
        base_url = request.form.get("create-manga-base")
        src_chap = request.form.get("create-manga-source-chap")
        base_chap = request.form.get("create-manga-base-chap")
        role_id = request.form.get("create-manga-role-id")
        channel_id = request.form.get("create-manga-channel-id")
        last_chapter_url = request.form.get("create-manga-last-chapter-url")
        tl_id = request.form.get("create-manga-tl-id")
        pr_id = request.form.get("create-manga-pr-id")
        clnr_id = request.form.get("create-manga-clnr-id")
        tser_id = request.form.get("create-manga-tser-id")
        category_id = request.form.get("create-manga-category-id")
        lr_id = request.form.get("create-manga-lastread-id")
        qc = int(request.form.get("create-manga-qc"))

        if not source_url or not base_url or not role_id or not channel_id:
            flash("All fields are mandatory!", category="error")
        else:
            payload = {
                "name": name,
                "image_url": img_url,
                "source_url": source_url,
                "base_url": base_url,
                "source_chap": src_chap,
                "base_chap": base_chap,
                "role_id": role_id,
                "channel_id": channel_id,
                "last_chapter_url": last_chapter_url,
                "main_category": category_id,
                "tl": tl_id,
                "pr": pr_id,
                "lr": lr_id,
                "clnr": clnr_id,
                "tser": tser_id,
                "qcer": qc
            }

            try:
                with rpost(f"http://{base_api_ip}/series/post/new/", json=payload) as response:
                    rcode = response.status_code
                    rheader = response.headers.get("short_code")

                if rcode != 200:
                    flash_texts = {
                        "mae": "Serie already exists!",
                        "wurl": "Wrong URl!",
                        "con": "Connection error. Please try again later."
                    }
                    flash(flash_texts[rheader], category="error")
                else:
                    flash("Serie added successfully!", category="success")
            except rConnErr:
                flash("API Connection error. Please try again later.", category="error")

    return render_template("create-manga.html", user=current_user)


@series_views.route("/delete-manga", methods=["POST", "GET"])
@login_required
def delete_manga():
    if request.method == "POST":
        aydi = request.form.get("delete-manga-id")

        if not aydi:
            flash("ID is mandatory!", category="error")
        else:
            with rget(f"http://{base_api_ip}/series/delete/{aydi}") as response:
                rtext = response.text
                rcode = response.status_code

            if rcode != 200:
                flash(f"An error occured.\nHTTP Code: {rcode}\nDetails: {rtext}", category="error")
            else:
                flash("Serie successfully deleted.", category="success")

    return render_template("delete-manga.html", user=current_user)


@series_views.route("/update-manga", methods=["POST", "GET"])
@login_required
def update_manga():
    if request.method == "POST":
        form = {
            "id": request.form.get("update-manga-id"),
            "name": request.form.get("update-manga-name"),
            "image_url": request.form.get("update-manga-imgurl"),
            "source_url": request.form.get("update-manga-sourceurl"),
            "base_url": request.form.get("update-manga-baseurl"),
            "source_chap": request.form.get("update-manga-lastsrc"),
            "base_chap": request.form.get("update-manga-lastbase"),
            "waiting_pr": request.form.get("update-manga-waitingpr"),
            "pred": request.form.get("update-manga-pred"),
            "last_readed": request.form.get("update-manga-last-read"),
            "cleaned": request.form.get("update-manga-cleaned"),
            "completed": request.form.get("update-manga-completed"),
            "role_id": request.form.get("update-manga-role-id"),
            "channel_id": request.form.get("update-manga-channel-id"),
            "main_category": request.form.get("update-manga-category-id"),
            "tl": request.form.get("update-manga-tl-id"),
            "pr": request.form.get("update-manga-pr-id"),
            "lr": request.form.get("update-manga-lastreader-id"),
            "clnr": request.form.get("update-manga-clnr-id"),
            "tser": request.form.get("update-manga-tser-id"),
            "qcer": request.form.get("update-manga-qc"),
            "last_qced": request.form.get("update-manga-last-qced"),
            "drive_url": request.form.get("update-manga-drive-url"),
        }

        if not form["id"]:
            flash("ID is mandatory!", category="error")
        else:
            payload = {}

            for key, value in form.items():
                if value:
                    payload[key] = value

            if not payload:
                flash("There is nothing to update!", category="info")
            else:
                try:
                    with rpost(f"http://{base_api_ip}/series/update/manga/", json=payload) as response:
                        rcode = response.status_code
                        rheader = response.headers.get("short_code")

                    if rcode != 200:
                        flash("Name or ID already exists!", category="error")
                    else:
                        flash("Serie updated successfully.", category="success")
                except rConnErr:
                    flash("API Connection error. Please try again later.", category="error")

    return render_template("update-manga.html", user=current_user)
