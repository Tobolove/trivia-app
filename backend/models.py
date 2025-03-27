import os
from sqlalchemy import Column, ForeignKey, String, Integer
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

database_name = os.environ.get('DB_NAME')
database_user = os.environ.get('DB_USER')
database_password = os.environ.get('DB_PASSWORD')
database_host = os.environ.get('DB_HOST')
database_port = os.environ.get('DB_PORT')
database_path = f'postgresql://{database_user}:{database_password}@{database_host}/{database_name}'

db = SQLAlchemy()

###----------------------------------------------------------------------------
###  Setup Database
###----------------------------------------------------------------------------

def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    with app.app_context():  
        db.create_all()


###----------------------------------------------------------------------------
###  Question Model
###----------------------------------------------------------------------------

class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(Integer, ForeignKey('categories.id'), nullable=False)
    difficulty = Column(Integer, nullable=False)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }

###----------------------------------------------------------------------------
###  Category odel
###----------------------------------------------------------------------------

class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)

    def __init__(self, type):
        self.type = type

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }
