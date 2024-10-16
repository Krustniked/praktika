import sqlite3
import codecs
from flask_sqlalchemy import SQLAlchemy
def create_date(db: SQLAlchemy):
    with codecs.open('data.db.sql', 'r','utf_8_sig') as sql_file:
                    sql_script = sql_file.read()
    dbs = sqlite3.connect('data.db')
    cursor = dbs.cursor()
    cursor.executescript(sql_script)
    dbs.commit()
    dbs.close()


'''from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from .models import Answer, Token

def create_date(db: SQLAlchemy):
    file = open("answer.sql", encoding="utf-8")
    txt = file.read()
    commands = txt.split(";")
    for command in commands:
        db.session.execute(text(command))'''