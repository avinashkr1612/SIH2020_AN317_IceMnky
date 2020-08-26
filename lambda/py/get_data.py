import json
import sys
import logging
import pymysql
import os


def initialize():
    rds_host = "sih-db.crvuwvincjld.us-east-1.rds.amazonaws.com"
    name = "admin"
    password = "killmonger"
    db_name = "sih20"

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    try:
        return pymysql.connect(
            rds_host,
            user=name,
            passwd=password,
            db=db_name,
            connect_timeout=5,
        )
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        return None


# Initialize the connection before program loads
connection = initialize()


def get_event_data(event):
    item_count = 0

    with connection.cursor() as cur:
        cur.execute("SELECT * FROM destination_info WHERE destination_id = '{}';".format(
            event['destID']),
        )
    
        row_headers=[x[0] for x in cur.description] 
        rv = cur.fetchall()
        json_data=[]

        for result in rv:
            json_data.append(dict(zip(row_headers,result)))

    return json_data


def add_latest_place_to_user(user_id, last_place):
    sql = (
        'INSERT INTO user_info (user_id, current_place) VALUES ("{0}", "{1}") '
        'ON DUPLICATE KEY UPDATE current_place="{1}"'
    ).format(user_id, last_place)

    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()

    return 

def add_user_phone_number(user_id, phone):
    sql = (
        'INSERT INTO emergency_info VALUES ("{0}", "{1}") '
        'ON DUPLICATE KEY UPDATE phone_no_list=CONCAT(phone_no_list, ";", "{1}")'
    ).format(user_id, phone)

    with connection.cursor() as cursor:
        cursor.execute(sql)

    connection.commit()

    return


def get_user_phone_emergency_number(user_id):
    sql = (
        'SELECT phone_no_list FROM emergency_info WHERE user_id="{0}"'
    ).format(user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        record = cursor.fetchone()
        return record[0]

    return None


def resolve_place(place_name):
    if not place_name:
        return place_name

    if 'taj' in place_name.lower():
        return 'tajmahal1663'

    return place_name


def get_latest_place_with_fallback(user_id, place):
    if place:
        return resolve_place(place)

    sql = (
        'SELECT current_place FROM user_info WHERE user_id="{0}"'
    ).format(user_id)

    with connection.cursor() as cursor:
        cursor.execute(sql)
        record = cursor.fetchone()

        if cursor.rowcount <= 0:
            return place

        return resolve_place(record[0])

    return resolve_place(place)
