from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app.models.user import User
from app.services.friend_service import FriendService

friends = Blueprint(
    "friends",
    __name__,
    url_prefix="/friends"
)


@friends.route("/", methods=["GET"])
@login_required
def search():

    query = request.args.get("q", "")

    users = FriendService.search_users(
        current_user,
        query
    )

    return render_template(
        "friends/search.html",
        users=users,
        query=query
    )


@friends.route("/send/<int:user_id>", methods=["POST"])
@login_required
def send_request(user_id):

    success, message = FriendService.send_request(
        current_user,
        user_id
    )

    flash(
        message,
        "success" if success else "error"
    )

    return redirect(
        url_for(
            "friends.search",
            q=request.args.get("q", "")
        )
    )

@friends.route("/requests")
@login_required
def requests():

    requests = FriendService.incoming_requests(
        current_user
    )

    return render_template(
        "friends/requests.html",
        requests=requests
    )


@friends.route("/accept/<int:request_id>", methods=["POST"])
@login_required
def accept(request_id):

    if not FriendService.accept_request(request_id, current_user.id):
        flash("This request is no longer available.", "error")
        return redirect(url_for("friends.requests"))

    flash(
        "Friend request accepted!",
        "success"
    )

    return redirect(
        url_for("friends.requests")
    )


@friends.route("/reject/<int:request_id>", methods=["POST"])
@login_required
def reject(request_id):

    if not FriendService.reject_request(request_id, current_user.id):
        flash("This request is no longer available.", "error")
        return redirect(url_for("friends.requests"))

    flash(
        "Friend request rejected.",
        "success"
    )

    return redirect(
        url_for("friends.requests")
    )

@friends.route("/list")
@login_required
def friends_list():

    friends = FriendService.friends_list(current_user)

    return render_template(
        "friends/list.html",
        friends=friends
    )
