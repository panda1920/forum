from flask import Flask
from config import Config

def setupApp():
    app = Flask(__name__)
    
    from routes import routes
    app.register_blueprint(routes)

    app.config.from_object(Config)

    return app