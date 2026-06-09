from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

# Defined once here, initialised in the app factory. This avoids circular imports.
db = SQLAlchemy()
jwt = JWTManager()
