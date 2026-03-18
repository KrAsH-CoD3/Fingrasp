from slowapi.util import get_remote_address
from slowapi import Limiter

# Define the limiter in a standalone module to prevent circular imports
# between the app factory and the routes.
limiter = Limiter(key_func=get_remote_address)
