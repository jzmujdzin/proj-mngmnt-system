import json
from typing import Tuple

import pandas as pd
import plotly
import plotly.express as px

from tools.db_connection import select_wrapper


@select_wrapper
def get_user_name(u_id: int) -> str:
    q = f"""
        SELECT name
        FROM userInfo
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_user_info(u_id: int) -> str:
    q = f"""
        SELECT *
        FROM userInfo
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_user_info_by_username(username: str) -> str:
    q = f"""
        SELECT ui.u_id, name, surname, address, pic_URL, role
        FROM userInfo ui
        JOIN users u ON ui.u_id = u.u_id
        JOIN userRoles ur ON ur.u_id = u.u_id
        JOIN roles r ON ur.role_id = r.role_id
        WHERE LOWER(username) = '{username.lower()}'
        """
    return q


@select_wrapper
def check_if_user_exists(username: str) -> str:
    q = f"""
        SELECT username
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_pwd_for_user_name(username: str) -> str:
    q = f"""
        SELECT password
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_pwd_for_u_id(u_id: int) -> str:
    q = f"""
        SELECT password
        FROM users
        WHERE u_id = {u_id};
        """
    return q


@select_wrapper
def get_user_id_for_username(username: str) -> str:
    q = f"""
        SELECT u_id
        FROM users
        WHERE username = '{username.lower()}';
        """
    return q


@select_wrapper
def get_projects_for_projects_screen(u_id: int) -> str:
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
def get_user_info_for_user_screen(u_id: int) -> str:
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
def get_customer_info_for_customer_screen(cust_name: str) -> str:
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
def get_project_info_for_in_depth_project_screen(p_id: int) -> str:
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
def get_users_from_list(u_list: str) -> str:
    usrs = "(" + ",".join(u_list) + ")"
    q = f"""
        SELECT name || ' ' || surname name, pic_URL, username
        FROM userInfo ui
        JOIN users u ON ui.u_id = u.u_id
        WHERE ui.u_id IN {usrs};
        """
    return q


@select_wrapper
def check_for_project_viewing_permissions(u_id: int, p_id: int) -> str:
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
def get_p_name(p_id: int) -> str:
    q = f"""
        SELECT p_name
        FROM projects p
        WHERE p_id = {p_id};
        """
    return q


@select_wrapper
def get_projects_for_customer(cust_id: int) -> str:
    q = f"""
        SELECT p_name, 
               p_id
        FROM projects
        WHERE cust_id = {cust_id};
        """
    return q


@select_wrapper
def get_roles_counts() -> str:
    q = """
        SELECT role, COUNT(*) number
        FROM userRoles ur
        JOIN roles r ON ur.role_id = r.role_id
        GROUP BY role
        ORDER BY number;
        """
    return q


@select_wrapper
def get_customer_project_counts() -> str:
    q = """
        SELECT name, COUNT(p_name) number
        FROM projects p
        JOIN customers c ON p.cust_id = c.cust_id
        GROUP BY name;
        """
    return q


@select_wrapper
def get_projects_assigned_users() -> str:
    q = """
        SELECT p_name, assigned_users
        FROM projectInfo pi
        JOIN projects p on pi.p_id = p.p_id;
        """
    return q


def get_projects_and_users_num() -> pd.DataFrame:
    df = get_projects_assigned_users()
    df["users_num"] = df["assigned_users"].apply(lambda x: len(x.split(",")))
    return df


def get_plots_for_dashboard() -> Tuple[str, str, str]:
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


@select_wrapper
def check_if_cust_name_exists(c_name: str) -> str:
    q = f"""
        SELECT name
        FROM customers
        WHERE LOWER(name) = '{c_name.lower()}';
        """
    return q


@select_wrapper
def check_if_proj_name_exists(p_name: str) -> str:
    q = f"""
        SELECT p_name
        FROM projects
        WHERE LOWER(p_name) = '{p_name.lower()}'
        """
    return q


@select_wrapper
def check_if_role_exists(role_name: str) -> str:
    q = f"""
        SELECT role_id
        FROM roles
        WHERE role = '{role_name}'
        """
    return q


@select_wrapper
def get_cust_id_for_cust_name(cust_name: str) -> str:
    q = f"""
        SELECT cust_id
        FROM customers
        WHERE LOWER(name) = '{cust_name.lower()}'
        """
    return q


@select_wrapper
def get_project_by_name(p_name: str) -> str:
    q = f"""
        SELECT p_id
        FROM projects
        WHERE LOWER(p_name) = '{p_name.lower()}'
        """
    return q


@select_wrapper
def check_user_edit_perm(u_id: int) -> str:
    q = f"""
        WITH editing_perm_lvl AS (
            SELECT permission_lvl
            FROM roles
            WHERE role = 'CEO'
        ),
        user_perm_lvl AS (
            SELECT permission_lvl
            FROM userRoles ur
            JOIN roles r ON ur.role_id = r.role_id
            WHERE u_id = {u_id}
            
        )
        SELECT epl.permission_lvl >= upl.permission_lvl has_sufficient_perm
        FROM editing_perm_lvl epl, user_perm_lvl upl
        """
    return q
