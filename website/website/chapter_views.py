from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from requests import get as rget, post as rpost, ConnectionError as rConnErr
from requests import patch as rpatch, delete as rdelete
from json import loads
from config import get_api_ip, get_timezone, get_locale

import arrow


chapter_views = Blueprint("chapter_views", __name__)

base_api_ip = get_api_ip()
time_zone = get_timezone()
locale = get_locale()


def _format_ch_times(uwu: list):
    for ch in uwu:
        if ch.get("created_at"):
            ch["created_at"] = arrow \
                .get(ch["created_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("closed_at"):
            ch["closed_at"] = arrow \
                .get(ch["closed_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("tl_at"):
            ch["tl_at"] = arrow \
                .get(ch["tl_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("pr_at"):
            ch["pr_at"] = arrow \
                .get(ch["pr_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("clnr_at"):
            ch["clnr_at"] = arrow \
                .get(ch["clnr_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("ts_at"):
            ch["ts_at"] = arrow \
                .get(ch["ts_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if ch.get("qc_at"):
            ch["qc_at"] = arrow \
                .get(ch["qc_at"], tzinfo="UTC") \
                .to(time_zone) \
                .format("D MMM YYYY - HH.mm", locale=locale)


@chapter_views.route("/all-chapters")
@login_required
def all_chapters():
    with rget(f"http://{base_api_ip}/chapters/get/") as response:
        rchapters = loads(response.text)["chapters"]

    _format_ch_times(rchapters)

    return render_template("chapters.html", user=current_user, chapters=rchapters)


@chapter_views.route("/open-chapters")
@login_required
def open_chapters():
    with rget(f"http://{base_api_ip}/chapters/get/filter-by/?params=closer_id%20IS%20NULL&count=1500") as response:
        rchapters = loads(response.text)["results"]

    _format_ch_times(rchapters)

    return render_template("chapters.html", user=current_user, chapters=rchapters)


@chapter_views.route("/last-period-chapters")
@login_required
def last_period_chapters():
    with rget(f"http://{base_api_ip}/chapters/get/last-period-chapters") as response:
        rchapters = loads(response.text)["chapters"]

    _format_ch_times(rchapters)

    return render_template("chapters.html", user=current_user, chapters=rchapters)


@chapter_views.route("add-chapter", methods=["POST", "GET"])
@login_required
def add_chapter():
    if request.method == "POST":
        create_time = int(arrow.utcnow().timestamp())
        payload = {
            "serie_id": request.form.get("create-chapter-serie-id"),
            "serie_name": request.form.get("create-chapter-serie-name"),
            "chapter_num": request.form.get("create-chapter-ch-no"),
            "creator_id": request.form.get("create-chapter-creator-id"),
            "creator_name": request.form.get("create-chapter-creator-name"),
            "created_at": create_time
        }

        try:
            with rpost(f"http://{base_api_ip}/chapters/new/", json=payload) as respose:
                if respose.status_code != 200:
                    flash(f"An error occured! Code: {respose.status_code}", category="error")
                else:
                    flash("Chaoter added successfully!", category="success")
        except rConnErr:
            flash("API connection error. Please try again later.", category="error")

    return render_template("create-chapter.html", user=current_user)


@chapter_views.route("update-chapter", methods=["POST", "GET"])
@login_required
def update_chapter():
    if request.method == "POST":
        form = {
            "id": request.form.get("update-chapter-id"),
            "serie_id": request.form.get("update-chapter-serie-id"),
            "serie_name": request.form.get("update-chapter-serie-name"),
            "chapter_num": request.form.get("update-chapter-chapter-no"),
            "creator_id": request.form.get("update-chapter-creator-id"),
            "creator_name": request.form.get("update-chapter-creator-name"),
            "tl_id": request.form.get("update-chapter-tl-id"),
            "tl_name": request.form.get("update-chapter-tl-name"),
            "tl_bytes": request.form.get("update-chapter-tl-bytes"),
            "pr_id": request.form.get("update-chapter-pr-id"),
            "pr_name": request.form.get("update-chapter-pr-name"),
            "clnr_id": request.form.get("update-chapter-clnr-id"),
            "clnr_name": request.form.get("update-chapter-clnr-name"),
            "ts_id": request.form.get("update-chapter-ts-id"),
            "ts_name": request.form.get("update-chapter-ts-name"),
            "qc_id": request.form.get("update-chapter-qc-id"),
            "qc_name": request.form.get("update-chapter-qc-name"),
        }

        if not form["id"]:
            flash("ID is mandatory!", category="error")
        else:
            payload = {}

            for key, value in form.items():
                if value:
                    payload[key] = value

            if form["tl_id"] == 1:
                payload["tl_at"] = int(arrow.utcnow().timestamp())
            if form["pr_id"] == 1:
                payload["pr_at"] = int(arrow.utcnow().timestamp())
            if form["clnr_id"] == 1:
                payload["clnr_at"] = int(arrow.utcnow().timestamp())
            if form["ts_id"] == 1:
                payload["ts_at"] = int(arrow.utcnow().timestamp())
            if form["qc_id"] == 1:
                payload["qc_at"] = int(arrow.utcnow().timestamp())

            if not payload:
                flash("No changes were entered to be updated.", category="info")
            else:
                try:
                    with rpatch(f"http://{base_api_ip}/chapters/update/", json=payload) as response:
                        if response.status_code != 200:
                            flash(f"Bir hata meydana geldi! Api kodu: {response.status_code}", category="error")
                            print(form)
                            print(payload)
                        else:
                            flash("Bölüm başarıyla güncellendi!", category="success")
                except rConnErr:
                    flash("API bağlantı problemi! Lütfen daha sonra tekrar deneyin.", category="error")

    return render_template("update-chapter.html", user=current_user)


@chapter_views.route("delete-chapter", methods=["POST", "GET"])
@login_required
def delete_chapter():
    if request.method == "POST":
        ch_id = request.form.get("delete-chapter-id")
        confirm = request.form.get("delete-all-chapters-confirm")
        if confirm:
            if confirm == "Yes.":
                with rdelete(f"http://{base_api_ip}/chapters/delete/") as response:
                    rcode = response.status_code
                    rtext = response.text
                    if rcode != 200:
                        flash(f"An error occured! Code: {rcode}\nDetails: {rtext}", category="error")
                    else:
                        flash("All chapters successfully deleted", category="success")
            else:
                flash("Be sure FFS!", category="error")
        else:
            if not ch_id:
                flash("ID is mandatory", category="error")
            else:
                with rdelete(f"http://{base_api_ip}/chapters/delete/{ch_id}") as response:
                    rcode = response.status_code
                    rtext = response.text

                    if rcode != 200:
                        flash(f"An error occured! Code: {rcode}\nDetails: {rtext}", category="error")
                    else:
                        flash("Chapter deleted successfully.", category="success")

    return render_template("delete-chapter.html", user=current_user)
