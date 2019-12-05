from flask import current_app

def getDB():
    return current_app.config['DATABASE_OBJECT']