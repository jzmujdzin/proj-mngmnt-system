from typing import Tuple

import pandas as pd
from werkzeug.security import check_password_hash, generate_password_hash

from queries.select_data import get_pwd_for_u_id, get_user_id_for_username
from tools.db_connection import tx_wrapper
from tools.table_data import Column


@tx_wrapper
def create_table_q(table_name: str, column_info: Tuple[Column]) -> str:
    """
    Creates query for table creation

    Using provided params, table_name and column_info, function iterates over columns in the column_info tuple,
    appends needed information to the query about column name and column data type.

    table_name: str -- name of the table
    column_info: Tuple[Column] -- tuple of Column dataclasses with column information (column_name and data type)

    Returns:
    String in the form of SQL query that when executed by cursor, creates the table
    """
    col_create = ""
    for column in column_info:
        col_create += f"""{column.column_name} {column.d_type} {',' if column.column_name != column_info[-1].column_name else ''}"""
    create_table_query = f"""
    CREATE TABLE {table_name} (
        {col_create}
    )
                         """
    return create_table_query


@tx_wrapper
def insert_values_q(table_name: str, df: pd.DataFrame) -> str:
    """
    Inserts values from dataframe into table

    Iterates over every row in the dataframe, checks its type and appends it to the query

    table_name: str -- name of the table
    df -- dataframe with data to insert to table

    Returns:
    String in the form of SQL query that when executed by cursor, inserts values into the table
    """
    values = ""
    columns = ""
    # iterates over columns and appends them to the columns string
    # df.columns.values returns i.e. array(['nums', 'letters'], dtype=object)
    # this converts it to (nums, letters) for applicable to be executed inside the query
    for col in df.columns.values:
        columns += col + ","
    # strips the last, obsolete comma
    columns = columns[:-1]
    # iterates over all rows
    for row in df.iterrows():
        row_values = "("
        # iterates over every cell
        for i in range(len(df.columns)):
            cell = row[1][i]
            # check if cell is the int type
            # this is needed because the string types should be input into query with apostrophes
            # i.e. we have two values, 'a' and 1
            # for a, it adds 'a' to query, for 1 it adds 1 to query
            if isinstance(cell, int):
                row_values += str(cell) + ","
            else:
                row_values += f""" '{str(cell)}',"""
        row_values = row_values[:-1]
        row_values += "),"
        values += row_values
    values = values[:-1]
    insert_values_query = f"""
    INSERT INTO {table_name}({columns})
    VALUES {values}
                           """
    return insert_values_query


@tx_wrapper
def create_email_validation_trigger():
    q = """
        CREATE TRIGGER validate_email_on_customerinfo_insertion
        BEFORE INSERT ON customerInfo
        BEGIN
           SELECT
              CASE
            WHEN NEW.email NOT LIKE '%_@__%.__%' THEN
              RAISE (ABORT,'Invalid email address')
               END;
        END;
        """
    return q


@tx_wrapper
def create_user_insert_trigger():
    q = """
        CREATE TRIGGER log_insertion_on_user_creation
        AFTER INSERT ON users
        BEGIN
            INSERT INTO logs (event_date, event, u_id)
            VALUES (datetime('now'), 'user creation', NEW.u_id);
        END ;
        """
    return q


@tx_wrapper
def create_user_pwd_update_trigger():
    q = """
        CREATE TRIGGER log_insertion_on_user_pwd_update
        BEFORE UPDATE ON users
        WHEN OLD.password <> NEW.password
        BEGIN
            INSERT INTO logs (event_date, event, u_id)
            VALUES (datetime('now'), 'user password change', OLD.u_id);
        END ;
        """
    return q


@tx_wrapper
def create_user_info_update_trigger():
    q = """
        CREATE TRIGGER log_insertion_on_user_info_update
        BEFORE UPDATE ON userInfo
        BEGIN 
            INSERT INTO logs (event_date, event, u_id)
            VALUES (datetime('now'), 'user info has changed: ' ||
             (CASE WHEN OLD.name <> NEW.name THEN 'user has changed name ' || OLD.name || ' to ' || NEW.name
             WHEN OLD.surname <> NEW.surname THEN 'user has changed surname ' || OLD.surname || ' to ' || NEW.surname
             WHEN OLD.address <> NEW.address THEN 'user has changed address ' || OLD.address || ' to ' || NEW.address 
             WHEN OLD.pic_URL <> NEW.pic_URL THEN 'user has changed pic_URL ' || OLD.pic_URL || ' to ' || NEW.pic_URL ELSE '' END ),
             OLD.u_id);
        END ;
        """
    return q


@tx_wrapper
def create_index(index_name: str, table_name: str, col_list: str):
    q = f"""
        CREATE INDEX {index_name}
        ON {table_name} ({col_list}); 
        """
    return q


def create_user(u_info: dict):
    insert_values_q(table_name="users", df=pd.DataFrame(u_info))
    fill_in_template = {
        "name": ["please fill in your name!"],
        "surname": ["please fill in your surname!"],
        "address": ["please fill in your address!"],
        "pic_url": [
            "https://www.seekpng.com/png/full/73-730482_existing-user-default-avatar.png"
        ],
    }
    fill_in_role = {
        "u_id": [get_user_id_for_username(u_info["username"][0])["u_id"][0]],
        "role_id": [4],
    }
    insert_values_q(table_name="userInfo", df=pd.DataFrame(fill_in_template))
    insert_values_q(table_name="userRoles", df=pd.DataFrame(fill_in_role))


def update_p_info(p_id: int, pname: str, pdesc: str):
    if pname != "":
        update_info(
            table_name="projects",
            set_what=f"""p_name = '{pname}' """,
            condition=f"p_id = {p_id}",
        )
    if pdesc != "":
        update_info(
            table_name="projectInfo",
            set_what=f""" p_long_description = '{pdesc}' """,
            condition=f"p_id = {p_id}",
        )


def update_c_info(
    c_name: str, c_address: str, c_email: str, c_phone: str, cust_id: int
):
    if c_name != "":
        update_info(
            table_name="customers",
            set_what=f"""name = '{c_name}' """,
            condition=f""" cust_id = {cust_id} """,
        )
    if c_address != "":
        update_info(
            table_name="customerInfo",
            set_what=f"""cust_address = '{c_address}' """,
            condition=f""" cust_id = {cust_id} """,
        )
    if c_email != "":
        update_info(
            table_name="customerInfo",
            set_what=f"""cust_email = '{c_email}' """,
            condition=f""" cust_id = {cust_id} """,
        )
    if c_phone != "":
        update_info(
            table_name="customerInfo",
            set_what=f"""cust_phone = '{c_phone}' """,
            condition=f""" cust_id = {cust_id} """,
        )


def update_u_info(name: str, surname: str, address: str, pic_URL: str, u_id: int):
    if name == "" and surname == "" and address == "" and pic_URL == "":
        return None
    if name != "":
        update_info(
            table_name="userInfo",
            set_what=f"""name = '{name}' """,
            condition=f"""u_id = {u_id} """,
        )
    if surname != "":
        update_info(
            table_name="userInfo",
            set_what=f"""surname = '{surname}' """,
            condition=f"""u_id = {u_id} """,
        )
    if address != "":
        update_info(
            table_name="userInfo",
            set_what=f"""address = '{address}' """,
            condition=f"""u_id = {u_id} """,
        )
    if pic_URL != "":
        update_info(
            table_name="userInfo",
            set_what=f"""pic_URL = '{pic_URL}' """,
            condition=f"""u_id = {u_id} """,
        )
    return True


def update_password(old_pwd: str, new_pwd: str, conf_new_pwd: str, u_id: int):
    if old_pwd == "" and new_pwd == "" and conf_new_pwd == "":
        return None
    if new_pwd != conf_new_pwd:
        return False
    if not check_password_hash(get_pwd_for_u_id(u_id)["password"][0], old_pwd):
        return False
    update_info(
        table_name="users",
        set_what=f"""password = '{generate_password_hash(new_pwd)}' """,
        condition=f"""u_id = {u_id} """,
    )
    return True


@tx_wrapper
def update_info(table_name: str, set_what: str, condition: str):
    q = f"""
        UPDATE {table_name}
        SET {set_what}
        WHERE {condition};
        """
    return q
