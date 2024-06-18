from aiohttp import web
from web.stream_routes import routes

# Create an aiohttp web application instance
web_app = web.Application()

# Add routes defined in web.stream_routes
web_app.add_routes(routes)

# Optionally, you can add middleware, error handling, etc., to the web application

# If you want to run the application directly from this file
if __name__ == "__main__":
    # Run the web application on localhost and port 8080
    web.run_app(web_app, host='localhost', port=8080)
