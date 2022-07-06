import sqlite3

conn = sqlite3.connect('deephelperbot.db')
cur = conn.cursor()


# user crud
def get_user(username):
    cur.execute(f'SELECT * FROM user WHERE nickname = "{username}"')
    return cur.fetchone()


def create_user(username):
    cur.execute(f'INSERT INTO user(nickname) VALUES ("{username}")')
    conn.commit()


# credit crud
def get_credit(owner_id, bank_name):
    cur.execute(f'SELECT * FROM credit WHERE owner_id = "{owner_id}" AND bank_name = "{bank_name}"')
    return cur.fetchone()


def create_credit(owner_id, bank_name, summ):
    cur.execute(f'INSERT INTO credit(owner_id, bank_name, summ) VALUES ("{owner_id}","{bank_name}","{summ}")')
    conn.commit()


def update_credit(owner_id, summ, bank):
    cur.execute(f'UPDATE credit SET summ = summ + {summ} WHERE owner_id = "{owner_id}" AND bank_name = "{bank}"')
    conn.commit()


def info_credit(owner_id):
    cur.execute(f'SELECT bank_name,summ FROM credit WHERE owner_id = "{owner_id}"')
    return cur.fetchall()


def summ_credit(owner_id):
    cur.execute(f'SELECT SUM(summ) FROM credit WHERE owner_id = "{owner_id}"')
    return cur.fetchone()


# requests crud
def get_request(owner_id, type_req, desc):
    cur.execute(f'SELECT * FROM help_requests WHERE owner_id = "{owner_id}" AND type = "{type_req}" AND description = "{desc}" ')
    return cur.fetchone()


def create_request(owner_id, type_req, description, attachments):
    cur.execute(f'INSERT INTO help_requests(owner_id, type, description, attachments) VALUES ("{owner_id}","{type_req}",'
                                                                                f'"{description}","{attachments}")')
    conn.commit()