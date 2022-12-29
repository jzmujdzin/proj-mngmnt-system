from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user
from werkzeug.security import check_password_hash, generate_password_hash

from queries.create_data import create_user
from queries.select_data import (check_for_project_editing_permissions,
                                 check_if_user_exists,
                                 get_project_info_for_in_depth_project_screen,
                                 get_projects_for_projects_screen,
                                 get_pwd_for_user_name,
                                 get_user_id_for_username, get_user_info,
                                 get_user_name, get_users_from_list)
from tools.models import User

app = Flask(__name__, template_folder="templates")
app.secret_key = "secretkey"
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(u_id):
    return User(**get_user_info(u_id).to_dict(orient="records")[0])


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    username = request.form.get("username")
    pwd = request.form.get("password")

    u_exists = check_if_user_exists(username)

    if u_exists.empty or not check_password_hash(
        get_pwd_for_user_name(username)["password"][0], pwd
    ):
        flash("wrong user - pwd combination. check your credentials and try again")
        return redirect(url_for("login"))

    u_id = get_user_id_for_username(username).iloc[0, 0]
    user = User(**get_user_info(u_id).to_dict(orient="records")[0])

    login_user(user)
    return redirect(url_for("projects"))


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup_post():
    u_info = {
        "username": [request.form.get("username")],
        "password": [generate_password_hash(request.form.get("password"))],
    }

    u_exists = check_if_user_exists(u_info["username"][0])
    if not u_exists.empty:
        flash("User with this username already exists. Try again.")
        return redirect(url_for("signup"))

    create_user(u_info)
    return redirect(url_for("login"))


@login_required
@app.route("/projects")
def projects():
    projects_dict = get_projects_for_projects_screen(current_user.u_id).to_dict(
        orient="index"
    )
    return render_template(
        "projects.html", name=current_user.name, projects_dict=projects_dict
    )


# check if user has permission to view this page. if yes -> render it normally. else -> throw error
@login_required
@app.route("/project-page/<int:p_id>")
def in_depth_project_page(p_id: int):
    p_info = get_project_info_for_in_depth_project_screen(p_id).iloc[0]
    assigned_u = get_users_from_list(p_info["assigned_users"].split(",")).to_dict(
        orient="index"
    )
    user_edit_perm = check_for_project_editing_permissions(
        current_user.u_id, p_id
    ).iloc[0]["has_sufficient_perm"]
    return render_template(
        "in-depth-project.html",
        p_info=p_info,
        assigned_u=assigned_u,
        user_edit_perm=user_edit_perm,
    )


# check if user has permission to view this page. if yes -> render it normally. else -> throw error
# @app.get('/project-page/{p_id}/{u_id}')
# def in_depth_project_page(request: Request, p_id: int, u_id: int):
#    p_info = get_project_info_for_in_depth_project_screen(p_id).iloc[0]
#    assigned_u = get_users_from_list(p_info['assigned_users'].split(',')).to_dict(orient='index')
#    user_edit_perm = check_for_project_editing_permissions(u_id, p_id).iloc[0]['has_sufficient_perm']
#    return templates.TemplateResponse('in-depth-project.html', {"request": request, "p_info": p_info, 'assigned_u': assigned_u, 'user_edit_perm': user_edit_perm})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
