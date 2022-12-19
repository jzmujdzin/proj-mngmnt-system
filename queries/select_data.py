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
def get_projects_for_projects_screen(u_id: int):
    q = f"""
        SELECT p_name, 
               p_short_description,
               c.name
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
def get_customer_info_for_customer_screen(cust_id: int):
    q = f"""
        SELECT name,
               cust_address,
               cust_email,
               cust_phone
        FROM customerInfo ci
        JOIN customers c on c.cust_id = ci.cust_id
        WHERE c.cust_id = {cust_id};
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
