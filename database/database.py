# This script is needed to create an empty database for summarization engine project.
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///summary.db'

db = SQLAlchemy(app)
db.init_app(app)


class Text(db.Model):
    __tablename__ = "text"

    # Initialize the Column
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    n_sentences = db.Column(db.Integer, nullable=False)
    n_words = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    # For displaying our database record rather than just numbers
    def __repr__(self):
        return '<Text %r>' % self.text


class Summary(db.Model):
    __tablename__ = "summary"

    # Initialize the Column
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    n_sentences = db.Column(db.Integer, nullable=False)
    n_words = db.Column(db.Integer, nullable=False)
    kind = db.Column(db.String(11), nullable=False)
    length_parameter = db.Column(db.Float(1), nullable=False)
    text = db.Column(db.Text, nullable=False)

    # For displaying our database record rather than just numbers
    def __repr__(self):
        return '<Summary %r>' % self.text


class Summarization(db.Model):
    __tablename__ = "summarization"

    # Initialize the Column
    id = db.Column(db.Integer, nullable=False, primary_key=True)
    text_id = db.Column(db.Integer, db.ForeignKey('text.id'), nullable=False)
    summary_id = db.Column(db.Integer, db.ForeignKey('summary.id'), nullable=False)
    datetime = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Float(5), nullable=False)
    rating = db.Column(db.Integer, nullable=True)

    # Initialize the relationship
    text = db.relationship('Text', backref="summarization")
    summary = db.relationship('Summary', backref="summarization")


if __name__ == '__main__':
    db.drop_all()  # emptying the db
    db.create_all()  # creating all tables and relationships
    db.session.commit()  # commit the changes
