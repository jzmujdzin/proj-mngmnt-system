from flask import (Flask, Response, flash, redirect, render_template, request,
                   url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

from queries.create_data import (create_customer, create_project, create_user,
                                 update_c_info, update_p_info, update_password,
                                 update_u_info, update_user_role)
from queries.select_data import (check_for_project_viewing_permissions,
                                 check_if_cust_name_exists,
                                 check_if_proj_name_exists,
                                 check_if_role_exists, check_if_user_exists,
                                 check_user_edit_perm,
                                 get_cust_id_for_cust_name,
                                 get_customer_info_for_customer_screen,
                                 get_plots_for_dashboard, get_project_by_name,
                                 get_project_info_for_in_depth_project_screen,
                                 get_projects_for_customer,
                                 get_projects_for_projects_screen,
                                 get_pwd_for_user_name,
                                 get_user_id_for_username, get_user_info,
                                 get_user_info_by_username,
                                 get_users_from_list)
from tools.models import User

app = Flask(__name__, template_folder="templates")
app.secret_key = "secretkey"
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(u_id: int) -> User:
    return User(**get_user_info(u_id).to_dict(orient="records")[0])


@app.route("/")
def root() -> Response:
    if current_user.is_authenticated:
        return redirect(url_for("projects"))
    return redirect(url_for("login"))


@app.route("/login")
def login() -> str:
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post() -> Response:
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
def signup() -> str:
    return render_template("signup.html")


@app.route("/signup", methods=["POST"])
def signup_post() -> Response:
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
def projects() -> str:
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
def in_depth_project_page(p_id: int) -> str:
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
def in_depth_project_page_post(p_id: int) -> Response:
    new_info = {
        "p_id": p_id,
        "pname": request.form.get("pname"),
        "pdesc": request.form.get("pdesc"),
    }
    update_p_info(**new_info)
    return redirect(url_for("in_depth_project_page", p_id=p_id))


@app.route("/user")
@login_required
def user() -> str:
    return render_template("user.html", cu=current_user, pic_link=current_user.pic_URL)


@app.route("/user/<string:username>")
@login_required
def user_page(username: str) -> str:
    user_info = get_user_info_by_username(username).to_dict(orient="index")[0]
    edit_permissions = check_user_edit_perm(current_user.u_id).iloc[0][
        "has_sufficient_perm"
    ]
    return render_template(
        "user_page.html",
        username=username,
        ui=user_info,
        pic_link=current_user.pic_URL,
        edit_permissions=edit_permissions,
    )


@app.route("/user/<string:username>", methods=["POST"])
def user_page_post(username: str) -> Response:
    r_exists = check_if_role_exists(request.form.get("role"))
    if r_exists.empty:
        flash("This role does not exist. Try different role.")
        return redirect(url_for("user_page", username=username))
    u_id = get_user_info_by_username(username).to_dict(orient="index")[0]["u_id"]
    update_user_role(r_exists.iloc[0]["role_id"], u_id)
    return redirect(url_for("user_page", username=username))


@app.route("/user", methods=["POST"])
def user_post() -> Response:
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
def customer(cust_name: str) -> str:
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
def customer_post(cust_name: str) -> Response:
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
def logout() -> Response:
    logout_user()
    flash("you have successfully logged out")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard() -> str:
    emp_roles_json, proj_cust_json, emp_proj_json = get_plots_for_dashboard()
    return render_template(
        "dashboard.html",
        emp_roles_json=emp_roles_json,
        proj_cust_json=proj_cust_json,
        emp_proj_json=emp_proj_json,
        pic_link=current_user.pic_URL,
    )


@app.route("/new/customer")
@login_required
def new_customer() -> str:
    return render_template(
        "new_customer.html",
        pic_link=current_user.pic_URL,
    )


@app.route("/new/customer", methods=["POST"])
def new_customer_post() -> Response:
    new_c = {
        "name": [request.form.get("c-name")],
    }
    new_c_info = {
        "cust_address": [request.form.get("c-address")],
        "cust_email": [request.form.get("c-mail")],
        "cust_phone": [request.form.get("c-phone")],
    }
    for dct in [new_c, new_c_info]:
        for k, v in dct.items():
            if v[0] == "":
                flash("Please fill in all fields.")
                return redirect(url_for("new_customer"))
    cust_exists = check_if_cust_name_exists(new_c["name"][0])
    if not cust_exists.empty:
        flash("Customer with this name exists. Try different name")
        return redirect(url_for("new_customer"))
    create_customer(new_c, new_c_info)
    return redirect(url_for("customer", cust_name=new_c["name"][0].lower()))


@app.route("/new/project")
@login_required
def new_project() -> str:
    return render_template(
        "new_project.html",
        pic_link=current_user.pic_URL,
    )


@app.route("/new/project", methods=["POST"])
def new_project_post() -> Response:
    new_p = {
        "p_name": [request.form.get("pname")],
        "cust_id": [request.form.get("cname")],
    }
    new_p_info = {
        "p_short_description": [request.form.get("pdesc-short")],
        "p_long_description": [request.form.get("pdesc-long")],
        "assigned_users": [request.form.get("resp-users")],
    }
    for dct in [new_p, new_p_info]:
        for k, v in dct.items():
            if v[0] == "":
                flash("Please fill in all fields.")
                return redirect(url_for("new_project"))
    try:
        new_p_perm = {"permission_lvl": [int(request.form.get("perm-lvl"))]}
    except ValueError:
        flash("Perm lvl should be a number. Try again.")
        return redirect(url_for("new_project"))
    p_exists = check_if_proj_name_exists(new_p["p_name"][0])
    if not p_exists.empty:
        flash("Project with this name exists. Try different name")
        return redirect(url_for("new_project"))
    c_id = get_cust_id_for_cust_name(new_p["cust_id"][0])
    if c_id.empty:
        flash("Could not find customer with this name. Try again.")
        return redirect(url_for("new_project"))
    new_p["cust_id"] = [c_id.iloc[0]["cust_id"]]
    create_project(new_p, new_p_info, new_p_perm)
    new_p_id = get_project_by_name(new_p["p_name"][0]).iloc[0]["p_id"]
    return redirect(url_for("in_depth_project_page", p_id=new_p_id))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
