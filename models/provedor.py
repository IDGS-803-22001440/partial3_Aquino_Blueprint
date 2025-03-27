from flask_sqlalchemy import SQLAlchemy
import datetime
db = SQLAlchemy()


# Modelo de Persona
class Provedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    telefono = db.Column(db.Integer, nullable=False)