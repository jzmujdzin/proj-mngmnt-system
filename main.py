from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

from queries.create_data import (create_user, update_c_info, update_p_info,
                                 update_password, update_u_info)
from queries.select_data import (check_for_project_viewing_permissions,
                                 check_if_user_exists,
                                 get_customer_info_for_customer_screen,
                                 get_plots_for_dashboard,
                                 get_project_info_for_in_depth_project_screen,
                                 get_projects_for_customer,
                                 get_projects_for_projects_screen,
                                 get_pwd_for_user_name,
                                 get_user_id_for_username, get_user_info,
                                 get_users_from_list)
from tools.models import User

app = Flask(__name__, template_folder="templates")
app.secret_key = "secretkey"
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(u_id):
    return User(**get_user_info(u_id).to_dict(orient="records")[0])


@app.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("projects"))
    return redirect(url_for("login"))


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
    user_to_login = User(**get_user_info(u_id).to_dict(orient="records")[0])

    login_user(user_to_login)
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


@app.route("/projects")
@login_required
def projects():
    projects_dict = get_projects_for_projects_screen(current_user.u_id).to_dict(
        orient="index"
    )
    return render_template(
        "projects.html",
        name=current_user.name,
        projects_dict=projects_dict,
        pic_link=current_user.pic_URL,
    )


@app.route("/project-page/<int:p_id>")
@login_required
def in_depth_project_page(p_id: int):
    p_info = get_project_info_for_in_depth_project_screen(p_id).iloc[0]
    assigned_u = get_users_from_list(p_info["assigned_users"].split(",")).to_dict(
        orient="index"
    )
    user_view_perm = check_for_project_viewing_permissions(
        current_user.u_id, p_id
    ).iloc[0]["has_sufficient_perm"]
    user_edit_perm = str(current_user.u_id) in p_info["assigned_users"].split(",")
    return render_template(
        "in-depth-project.html",
        p_id=p_id,
        p_info=p_info,
        assigned_u=assigned_u,
        user_edit_perm=user_edit_perm,
        user_view_perm=user_view_perm,
        pic_link=current_user.pic_URL,
    )


@app.route("/project-page/<int:p_id>", methods=["POST"])
def in_depth_project_page_post(p_id: int):
    new_info = {
        "p_id": p_id,
        "pname": request.form.get("pname"),
        "pdesc": request.form.get("pdesc"),
    }
    update_p_info(**new_info)
    return redirect(url_for("in_depth_project_page", p_id=p_id))


@app.route("/user")
@login_required
def user():
    return render_template("user.html", cu=current_user, pic_link=current_user.pic_URL)


@app.route("/user", methods=["POST"])
def user_post():
    new_info = {
        "name": request.form.get("u-name"),
        "surname": request.form.get("u-surname"),
        "address": request.form.get("u-address"),
        "pic_URL": request.form.get("u-pic"),
        "u_id": current_user.u_id,
    }
    pwd_info = {
        "old_pwd": request.form.get("old-pwd"),
        "new_pwd": request.form.get("new-pwd"),
        "conf_new_pwd": request.form.get("conf-new-pwd"),
        "u_id": current_user.u_id,
    }
    if update_u_info(**new_info):
        flash("Updated user information", "success")
    update_pwd_info = update_password(**pwd_info)
    if update_pwd_info:
        flash("Password changed succesfully.", "success")
    elif update_pwd_info is False:
        flash(
            "Wrong old password or new password and password confirmation did not match. Try again.",
            "error",
        )
    return redirect(url_for("user"))


@app.route("/customer/<string:cust_name>")
@login_required
def customer(cust_name: str):
    c_info = get_customer_info_for_customer_screen(cust_name).iloc[0]
    cust_projects = get_projects_for_customer(c_info["cust_id"]).to_dict(orient="index")
    return render_template(
        "customer.html",
        c_info=c_info,
        cust_projects=cust_projects,
        cust_name=cust_name,
        pic_link=current_user.pic_URL,
    )


@app.route("/customer/<string:cust_name>", methods=["POST"])
def customer_post(cust_name: str):
    new_info = {
        "c_name": request.form.get("c-name"),
        "c_address": request.form.get("c-address"),
        "c_email": request.form.get("c-mail"),
        "c_phone": request.form.get("c-phone"),
        "cust_id": get_customer_info_for_customer_screen(cust_name).iloc[0]["cust_id"],
    }
    update_c_info(**new_info)
    return redirect(url_for("customer", cust_name=cust_name))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("you have successfully logged out")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    emp_roles_json, proj_cust_json, emp_proj_json = get_plots_for_dashboard()
    return render_template(
        "dashboard.html",
        emp_roles_json=emp_roles_json,
        proj_cust_json=proj_cust_json,
        emp_proj_json=emp_proj_json,
        pic_link=current_user.pic_URL,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
