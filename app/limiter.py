from slowapi import Limiter

# Import the project's real IP function that respects proxy headers
from app.security import get_real_ip

# Define the limiter in a standalone module to prevent circular imports
# between the app factory and the routes.
# Use get_real_ip to correctly identify users behind Cloudflare/reverse proxies.
limiter = Limiter(key_func=get_real_ip)
