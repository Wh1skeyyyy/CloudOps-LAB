from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy

# Defined once here, initialised in the app factory. This avoids circular imports.
db = SQLAlchemy()
jwt = JWTManager()

# Rate limiter keyed by client IP. memory:// storage is fine for a single
# process; a multi-instance deployment would use Redis so all workers share
# counts. No default_limits set — only routes we decorate are limited.
limiter = Limiter(key_func=get_remote_address, storage_uri="memory://")
