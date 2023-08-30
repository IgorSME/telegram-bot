# import config
# import psycopg2
#
#
# def create_table_agents():
#     con = psycopg2.connect(host=config.PostgreSQL['host'], user=config.PostgreSQL['user'], passwd=config.PostgreSQL['password'], db=config.PostgreSQL['database'])
#     cur = con.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS agents(id SERIAL PRIMARY KEY, agent_id TEXT)")
#
#     cur.close()
#     con.close()
#
#
# def create_table_passwords():
#     con = psycopg2.connect(host=config.PostgreSQL['host'], user=config.PostgreSQL['user'], passwd=config.PostgreSQL['password'], db=config.PostgreSQL['database'])
#     cur = con.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS passwords(id SERIAL PRIMARY KEY, password TEXT)")
#
#     cur.close()
#     con.close()
#
#
# def create_table_files():
#     con = psycopg2.connect(host=config.PostgreSQL['host'], user=config.PostgreSQL['user'], passwd=config.PostgreSQL['password'], db=config.PostgreSQL['database'])
#     cur = con.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS files(id SERIAL PRIMARY KEY, req_id TEXT, file_id TEXT, file_name TEXT, type TEXT)")
#
#     cur.close()
#     con.close()
#
#
# def create_table_requests():
#     con = psycopg2.connect(host=config.PostgreSQL['host'], user=config.PostgreSQL['user'], passwd=config.PostgreSQL['password'], db=config.PostgreSQL['database'])
#     cur = con.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS requests(req_id SERIAL PRIMARY KEY, user_id TEXT, req_status TEXT)")
#
#     cur.close()
#     con.close()
#
#
# def create_table_messages():
#     con = psycopg2.connect(host=config.PostgreSQL['host'], user=config.PostgreSQL['user'], passwd=config.PostgreSQL['password'], db=config.PostgreSQL['database'])
#     cur = con.cursor()
#
#     cur.execute("CREATE TABLE IF NOT EXISTS messages(id SERIAL PRIMARY KEY, req_id TEXT, message TEXT, user_status TEXT, date TEXT)")
#
#     cur.close()
#     con.close()
#
#
#
# create_table_agents()
# create_table_passwords()
# create_table_files()
# create_table_requests()
# create_table_messages()

import config
import psycopg2

def create_tables():
    con = psycopg2.connect(
        host=config.PostgreSQL['host'],
        user=config.PostgreSQL['user'],
        password=config.PostgreSQL['password'],
        dbname=config.PostgreSQL['database']
    )
    cur = con.cursor()

    queries = [
        "CREATE TABLE IF NOT EXISTS agents(id SERIAL PRIMARY KEY, agent_id TEXT)",
        "CREATE TABLE IF NOT EXISTS passwords(id SERIAL PRIMARY KEY, password TEXT)",
        "CREATE TABLE IF NOT EXISTS files(id SERIAL PRIMARY KEY, req_id TEXT, file_id TEXT, file_name TEXT, type TEXT)",
        "CREATE TABLE IF NOT EXISTS requests(req_id SERIAL PRIMARY KEY, user_id TEXT, req_status TEXT, agent_id TEXT)",
        "CREATE TABLE IF NOT EXISTS messages(id SERIAL PRIMARY KEY, req_id TEXT, message TEXT, user_status TEXT, date TEXT)"
    ]

    for query in queries:
        cur.execute(query)

    con.commit()
    cur.close()
    con.close()

create_tables()
