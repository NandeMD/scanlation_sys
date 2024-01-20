from flask import Blueprint, render_template, request, flash, session
from flask_login import login_required, current_user
from requests import get as rget, post as rpost, ConnectionError as rConnErr
from requests import patch as rpatch, delete as rdelete
from json import loads
from config import get_api_ip, get_locale, get_timezone

import arrow


payperiod_views = Blueprint("payperiod_views", __name__)

base_api_ip = get_api_ip()
tz = get_timezone()
locale = get_locale()


def _format_period_times(owo: list):
    for p in owo:
        if p.get("created_at"):
            p["created_at"] = arrow \
                .get(p["created_at"], tzinfo="UTC") \
                .to(tz) \
                .format("D MMM YYYY - HH.mm", locale=locale)
        if p.get("closed_at"):
            p["closed_at"] = arrow \
                .get(p["closed_at"], tzinfo="UTC") \
                .to(tz) \
                .format("D MMM YYYY - HH.mm", locale=locale)


@payperiod_views.route("all-periods")
@login_required
def all_periods():
    with rget(f"http://{base_api_ip}/payperiods/get/") as response:
        rperiods = loads(response.text)["periods"]

    _format_period_times(rperiods)

    return render_template("payperiods.html", user=current_user, payment_periods=rperiods)


@payperiod_views.route("last-period")
@login_required
def last_period():
    with rget(f"http://{base_api_ip}/payperiods/get/last-period") as response:
        p = [loads(response.text)["pay_period"]]

    _format_period_times(p)

    return render_template("payperiods.html", user=current_user, payment_periods=p)


@payperiod_views.route("/create-period", methods=["POST", "GET"])
@login_required
def create_period():
    if request.method == "POST":
        creator_id = request.form.get("create-period-creator-id")
        creator_name = request.form.get("create-period-creator-name")
        created_at = int(arrow.utcnow().timestamp())

        payload = {
            "creator_id": creator_id,
            "creator_name": creator_name,
            "created_at": created_at
        }

        with rpost(f"http://{base_api_ip}/payperiods/new/", json=payload) as response:
            rcode = response.status_code
            rtext = response.text

            if rcode != 200:
                flash(f"An error occured!\nHTTP Code: {rcode}\nDetails: {rtext}", category="error")
            else:
                flash("Payment period successfully created!", category="success")

    return render_template("create-period.html", user=current_user)


# noinspection DuplicatedCode
@payperiod_views.route("/update-period", methods=["POST", "GET"])
@login_required
def update_period():
    if request.method == "POST":
        cr_at = request.form.get("update-period-created-at")
        cl_at = request.form.get("update-period-closed-at")
        form = {
            "id": request.form.get("update-period-id"),
            "creator_id": request.form.get("update-period-creator-id"),
            "creator_name": request.form.get("update-period-cretor-name"),
            "created_at": int(arrow.get(cr_at, tzinfo=tz).to("utc").timestamp()) if cr_at else False,
            "closer_id": request.form.get("update-period-closer-id"),
            "closer_name": request.form.get("update-period-closer-name"),
            "closed_at": int(arrow.get(cl_at, tzinfo=tz).to("utc").timestamp()) if cl_at else False
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
                    with rpatch(f"http://{base_api_ip}/payperiods/update/", json=payload) as response:
                        if response.status_code != 200:
                            flash(f"An error occured. Code: {response.status_code}", category="error")
                            print(form)
                            print(payload)
                        else:
                            flash("Period successfully updated", category="success")
                except rConnErr:
                    flash("Api connection error. Please try again later.", category="error")

    return render_template("update-period.html", user=current_user)


# noinspection DuplicatedCode
@payperiod_views.route("delete-period", methods=["POST", "GET"])
@login_required
def delete_period():
    if request.method == "POST":
        ch_id = request.form.get("delete-period-id")
        confirm = request.form.get("delete-all-periods-confirm")
        if confirm:
            if confirm == "Evet.":
                with rdelete(f"http://{base_api_ip}/payperiods/delete/") as response:
                    rcode = response.status_code
                    rtext = response.text
                    if rcode != 200:
                        flash(f"An error occured!\nHTTP Code: {rcode}\nDetails: {rtext}", category="error")
                    else:
                        flash("All periods successfully deleted.", category="success")
            else:
                flash("Be sure FFS!", category="error")
        else:
            if not ch_id:
                flash("ID is mandatory.", category="error")
            else:
                with rdelete(f"http://{base_api_ip}/payperiods/delete/{ch_id}") as response:
                    rcode = response.status_code
                    rtext = response.text

                    if rcode != 200:
                        flash(f"An error occured!\nHTTP Code: {rcode}\nDetails: {rtext}", category="error")
                    else:
                        flash("Period successfully deleted.", category="success")

    return render_template("delete-period.html", user=current_user)
