import json

import plotly
import plotly.express as px

from tools.db_connection import select_wrapper


@select_wrapper
def get_user_name(u_id: int):
    q = f"""
        SELECT name
        FROM userInfo
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_user_info(u_id: int):
    q = f"""
        SELECT *
        FROM userInfo
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def check_if_user_exists(username: str):
    q = f"""
        SELECT username
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_pwd_for_user_name(username: str):
    q = f"""
        SELECT password
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_pwd_for_u_id(u_id: int):
    q = f"""
        SELECT password
        FROM users
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_user_id_for_username(username: str):
    q = f"""
        SELECT u_id
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_projects_for_projects_screen(u_id: int):
    q = f"""
        SELECT p_name, 
               p_short_description,
               c.name,
               p.p_id,
               c.cust_id
        FROM projects p
        JOIN customers c ON p.cust_id = c.cust_id
        JOIN projectInfo pi ON pi.p_id = p.p_id
        WHERE p.p_id IN
        (
            SELECT pi.p_id
            FROM projectInfo pi
            JOIN projectPermissions pp ON  pi.p_id = pp.p_id
            WHERE permission_lvl >= 
                (
                SELECT permission_lvl
                FROM userRoles ur
                JOIN roles r on ur.role_id = r.role_id
                WHERE u_id = {u_id}
                )
        );
        """
    return q


@select_wrapper
def get_user_info_for_user_screen(u_id: int):
    q = f"""
        SELECT name,
               surname,
               address,
               pic_URL
        FROM userInfo
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_customer_info_for_customer_screen(cust_name: str):
    q = f"""
        SELECT name,
               c.cust_id,
               cust_address,
               cust_email,
               cust_phone
        FROM customerInfo ci
        JOIN customers c on c.cust_id = ci.cust_id
        WHERE LOWER(name) = '{cust_name.lower()}';
        """
    return q


@select_wrapper
def get_project_info_for_in_depth_project_screen(p_id: int):
    q = f"""
        SELECT p_name,
        (SELECT name FROM customers WHERE cust_id = (SELECT cust_id FROM projects WHERE p_id = {p_id})) customer,
        p_long_description,
        assigned_users
        FROM projectInfo pi
        JOIN projects p on pi.p_id = p.p_id
        WHERE pi.p_id = {p_id};
        """
    return q


@select_wrapper
def get_users_from_list(u_list: str):
    usrs = "(" + ",".join(u_list) + ")"
    q = f"""
        SELECT name || ' ' || surname name, pic_URL
        FROM userInfo
        WHERE u_id IN {usrs};
        """
    return q


@select_wrapper
def check_for_project_viewing_permissions(u_id: int, p_id: int):
    q = f"""
        WITH user_permission_lvl AS (
        SELECT permission_lvl
        FROM userRoles ur
        JOIN roles r ON ur.role_id = r.role_id
        WHERE u_id = {u_id}
        ),
        project_permission_lvl AS (
        SELECT permission_lvl
        FROM projectPermissions
        WHERE p_id = {p_id}
        )
        SELECT upl.permission_lvl <= ppl.permission_lvl has_sufficient_perm
        FROM user_permission_lvl upl, project_permission_lvl ppl;
        """
    return q


@select_wrapper
def get_p_name(p_id: int):
    q = f"""
        SELECT p_name
        FROM projects p
        WHERE p_id = {p_id};
        """
    return q


@select_wrapper
def get_projects_for_customer(cust_id: int):
    q = f"""
        SELECT p_name, 
               p_id
        FROM projects
        WHERE cust_id = {cust_id};
        """
    return q


@select_wrapper
def get_roles_counts():
    q = """
        SELECT role, COUNT(*) number
        FROM userRoles ur
        JOIN roles r ON ur.role_id = r.role_id
        GROUP BY role
        ORDER BY number;
        """
    return q


@select_wrapper
def get_customer_project_counts():
    q = """
        SELECT name, COUNT(p_name) number
        FROM projects p
        JOIN customers c ON p.cust_id = c.cust_id
        GROUP BY name;
        """
    return q


@select_wrapper
def get_projects_assigned_users():
    q = """
        SELECT p_name, assigned_users
        FROM projectInfo pi
        JOIN projects p on pi.p_id = p.p_id;
        """
    return q


def get_projects_and_users_num():
    df = get_projects_assigned_users()
    df["users_num"] = df["assigned_users"].apply(lambda x: len(x.split(",")))
    return df


def get_plots_for_dashboard():
    employee_roles = get_roles_counts()
    projects_customers = get_customer_project_counts()
    employee_projects = get_projects_and_users_num()
    fig_emp_roles = px.bar(employee_roles, x="role", y="number")
    fig_proj_cust = px.bar(projects_customers, x="name", y="number")
    fig_emp_proj = px.bar(employee_projects, x="p_name", y="users_num")
    plot_layout_dict = {
        "plot_bgcolor": "#808080",
        "paper_bgcolor": "#808080",
        "title_x": 0.5,
        "font": {"family": "Arial Black", "color": "black"},
    }
    fig_emp_roles.update_layout(title="<b>Roles by employee count</b>")
    fig_emp_roles.update_layout(plot_layout_dict)
    fig_proj_cust.update_layout(title="<b>Projects for each customer</b>")
    fig_proj_cust.update_layout(plot_layout_dict)
    fig_emp_proj.update_layout(title="<b>Users assigned for each project</b>")
    fig_emp_proj.update_layout(plot_layout_dict)
    emp_roles_json = json.dumps(fig_emp_roles, cls=plotly.utils.PlotlyJSONEncoder)
    proj_cust_json = json.dumps(fig_proj_cust, cls=plotly.utils.PlotlyJSONEncoder)
    emp_proj_json = json.dumps(fig_emp_proj, cls=plotly.utils.PlotlyJSONEncoder)
    return emp_roles_json, proj_cust_json, emp_proj_json
