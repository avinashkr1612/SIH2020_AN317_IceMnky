import json
import sys
import logging
import pymysql
import os

def _handler(event):
    rds_host  = os.getenv("RDS_HOST")
    name = os.getenv("NAME")
    password = os.getenv("PASSWORD")
    db_name = os.getenv("DB_NAME")
    
    
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    try:
        conn = pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
        
    logger.info("SUCCESS: Connection to RDS MySQL instance succeeded")
    item_count = 0
    
    with conn.cursor() as cur:
        cur.execute("select * from destination_info where destination_id = '{}';".format(event['destID']))
        row_headers=[x[0] for x in cur.description] 
        rv = cur.fetchall()
        json_data=[]
        for result in rv:
            json_data.append(dict(zip(row_headers,result)))
    conn.commit()

    return json_data
    
    