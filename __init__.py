from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import database_exists, create_database
from models import Base
from sqlalchemy import create_engine

from .create_sql import create_date



db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/data.db"
    db.init_app(app)
    with app.app_context():
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])
            Base.metadata.create_all(bind=create_engine(app.config['SQLALCHEMY_DATABASE_URI']))
            create_date(db)
            
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
   
    

    
    return app


