from flask import Flask

def setupApp():
    app = Flask(__name__)
    
    from routes import routes
    app.register_blueprint(routes)

    from mongodb import MongoDB
    app.config['DATABASE_OBJECT'] = MongoDB()

    return app