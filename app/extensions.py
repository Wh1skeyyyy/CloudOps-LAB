from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Defined once here, initialised in the app factory. This avoids circular imports.
db = SQLAlchemy()
jwt = JWTManager()
