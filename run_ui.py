"""
Adversys Core Integration Changes:
==================================
This file has been modified for integration with adversys-core. The following changes were made:

1. BASE_PATH Hardcoding:
   - BASE_PATH is hardcoded to "/delta" (previously read from DELTA_BASE_PATH env var)
   - All Flask routes are registered with /delta/ prefix (API endpoints, UI routes, login/logout)
   - Middleware routes (/mcp, /a2a) are registered with /delta/ prefix
   - Static file serving uses /delta/ as the base path

2. JavaScript Integration:
   - Injects window.deltaBasePath = "/delta" into HTML for frontend API calls
   - Injects window.__disableServiceWorker = true to disable service workers (avoids reverse proxy issues)

3. Route Registration:
   - All API handlers registered at /delta/{name} instead of /{name}
   - Login/logout routes at /delta/login and /delta/logout
   - Root route at /delta/ instead of /

These changes allow Delta to work seamlessly behind adversys-core's nginx reverse proxy
without requiring path rewriting. All paths are handled consistently at the application level.
"""

import asyncio
from datetime import timedelta
import os
import secrets
import hashlib
import time
import socket
import struct
from functools import wraps
import threading
from flask import Flask, request, Response, session, redirect, url_for, render_template_string
from werkzeug.wrappers.response import Response as BaseResponse
import initialize
from python.helpers import files, git, mcp_server, fasta2a_server
from python.helpers.files import get_abs_path
from python.helpers import runtime, dotenv, process
from python.helpers.extract_tools import load_classes_from_folder
from python.helpers.api import ApiHandler
from python.helpers.print_style import PrintStyle
from python.helpers import login

# disable logging
import logging
logging.getLogger().setLevel(logging.WARNING)


# Set the new timezone to 'UTC'
os.environ["TZ"] = "UTC"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
# Apply the timezone change
if hasattr(time, 'tzset'):
    time.tzset()

# Adversys Added this: Base path for Delta when integrated with adversys-core
# Hardcoded to /delta since it will never change in adversys-core integration
BASE_PATH = "/delta"

# Adversys Added this: Clear AUTH_LOGIN from .env file if explicitly set to empty in environment
# Clear AUTH_LOGIN from .env file if explicitly set to empty in environment
# This ensures authentication is disabled when integrated with Adversys
if os.getenv("AUTH_LOGIN") == "":
    try:
        from python.helpers import dotenv
        dotenv.load_dotenv()
        # Remove AUTH_LOGIN and AUTH_PASSWORD from .env file if they exist
        dotenv_path = dotenv.get_dotenv_file_path()
        if os.path.isfile(dotenv_path):
            import re
            with open(dotenv_path, "r") as f:
                lines = f.readlines()
            with open(dotenv_path, "w") as f:
                for line in lines:
                    # Skip lines that set AUTH_LOGIN or AUTH_PASSWORD to empty or any value
                    if not re.match(r"^\s*(AUTH_LOGIN|AUTH_PASSWORD)\s*=", line):
                        f.write(line)
            dotenv.load_dotenv()
    except Exception:
        pass  # If we can't clear it, continue anyway

# initialize the internal Flask server
# Use BASE_PATH for static files so they're served at the correct path
webapp = Flask("app", static_folder=get_abs_path("./webui"), static_url_path=BASE_PATH if BASE_PATH else "/")
webapp.secret_key = os.getenv("FLASK_SECRET_KEY") or secrets.token_hex(32)
webapp.config.update(
    JSON_SORT_KEYS=False,
    SESSION_COOKIE_NAME="session_" + runtime.get_runtime_id(),  # bind the session cookie name to runtime id to prevent session collision on same host
    SESSION_COOKIE_SAMESITE="Strict",
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=1)
)

lock = threading.Lock()

# Set up basic authentication for UI and API but not MCP
# basic_auth = BasicAuth(webapp)


def is_loopback_address(address):
    loopback_checker = {
        socket.AF_INET: lambda x: struct.unpack("!I", socket.inet_aton(x))[0]
        >> (32 - 8)
        == 127,
        socket.AF_INET6: lambda x: x == "::1",
    }
    address_type = "hostname"
    try:
        socket.inet_pton(socket.AF_INET6, address)
        address_type = "ipv6"
    except socket.error:
        try:
            socket.inet_pton(socket.AF_INET, address)
            address_type = "ipv4"
        except socket.error:
            address_type = "hostname"

    if address_type == "ipv4":
        return loopback_checker[socket.AF_INET](address)
    elif address_type == "ipv6":
        return loopback_checker[socket.AF_INET6](address)
    else:
        for family in (socket.AF_INET, socket.AF_INET6):
            try:
                r = socket.getaddrinfo(address, None, family, socket.SOCK_STREAM)
            except socket.gaierror:
                return False
            for family, _, _, _, sockaddr in r:
                if not loopback_checker[family](sockaddr[0]):
                    return False
        return True

def requires_api_key(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # Use the auth token from settings (same as MCP server)
        from python.helpers.settings import get_settings
        valid_api_key = get_settings()["mcp_server_token"]

        if api_key := request.headers.get("X-API-KEY"):
            if api_key != valid_api_key:
                return Response("Invalid API key", 401)
        elif request.json and request.json.get("api_key"):
            api_key = request.json.get("api_key")
            if api_key != valid_api_key:
                return Response("Invalid API key", 401)
        else:
            return Response("API key required", 401)
        return await f(*args, **kwargs)

    return decorated


# allow only loopback addresses
def requires_loopback(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not is_loopback_address(request.remote_addr):
            return Response(
                "Access denied.",
                403,
                {},
            )
        return await f(*args, **kwargs)

    return decorated


# require authentication for handlers
def requires_auth(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        user_pass_hash = login.get_credentials_hash()
        # If no auth is configured, just proceed
        if not user_pass_hash:
            return await f(*args, **kwargs)

        if session.get('authentication') != user_pass_hash:
            return redirect(url_for('login_handler'))
        
        return await f(*args, **kwargs)

    return decorated

def csrf_protect(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        token = session.get("csrf_token")
        header = request.headers.get("X-CSRF-Token")
        cookie = request.cookies.get("csrf_token_" + runtime.get_runtime_id())
        sent = header or cookie
        if not token or not sent or token != sent:
            return Response("CSRF token missing or invalid", 403)
        return await f(*args, **kwargs)

    return decorated

@webapp.route(f"{BASE_PATH}/login", methods=["GET", "POST"])
async def login_handler():
    error = None
    if request.method == 'POST':
        user = dotenv.get_dotenv_value("AUTH_LOGIN")
        password = dotenv.get_dotenv_value("AUTH_PASSWORD")
        
        if request.form['username'] == user and request.form['password'] == password:
            session['authentication'] = login.get_credentials_hash()
            return redirect(url_for('serve_index'))
        else:
            error = 'Invalid Credentials. Please try again.'
            
    login_page_content = files.read_file("webui/login.html")
    return render_template_string(login_page_content, error=error)

@webapp.route(f"{BASE_PATH}/logout")
async def logout_handler():
    session.pop('authentication', None)
    return redirect(url_for('login_handler'))

# Adversys Added this: Route handler for source maps (/sm/...)
# Source maps are referenced in minified CSS/JS files and need to be accessible under /delta/sm/
@webapp.route(f"{BASE_PATH}/sm/<path:filename>")
async def serve_source_map(filename):
    """Serve source map files from the static folder"""
    return webapp.send_static_file(f"sm/{filename}")

# handle default address, load index
@webapp.route(f"{BASE_PATH}/", methods=["GET"])
@requires_auth
async def serve_index():
    gitinfo = None
    try:
        gitinfo = git.get_git_info()
    except Exception:
        gitinfo = {
            "version": "unknown",
            "commit_time": "unknown",
        }
    index = files.read_file("webui/index.html")
    index = files.replace_placeholders_text(
        _content=index,
        version_no=gitinfo["version"],
        version_time=gitinfo["commit_time"]
    )
    # Adversys Added this: Add base tag and disable service worker script
    # The base tag ensures relative paths resolve correctly under /delta/
    # ES module imports are handled by Import Maps in index.html
    base_tag = f'<base href="{BASE_PATH}/">'
    script_tag = '<script>window.__disableServiceWorker = true;</script>'
    index = index.replace('<head>', f'<head>\n    {base_tag}\n    {script_tag}', 1)
    
    return index

def run():
    PrintStyle().print("Initializing framework...")

    # Suppress only request logs but keep the startup messages
    from werkzeug.serving import WSGIRequestHandler
    from werkzeug.serving import make_server
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from a2wsgi import ASGIMiddleware
    import logging
    
    #Adversys Added this: Suppress Werkzeug development server warning
    # Silence Werkzeug development server warning
    # This is the official Agent Zero setup, and it's fine behind Nginx
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    PrintStyle().print("Starting server...")

    class NoRequestLoggingWSGIRequestHandler(WSGIRequestHandler):
        def log_request(self, code="-", size="-"):
            pass  # Override to suppress request logging

    # Get configuration from environment
    port = runtime.get_web_ui_port()
    host = (
        runtime.get_arg("host") or dotenv.get_dotenv_value("WEB_UI_HOST") or "localhost"
    )
    server = None

    def register_api_handler(app, handler: type[ApiHandler]):
        name = handler.__module__.split(".")[-1]
        instance = handler(app, lock)

        async def handler_wrap() -> BaseResponse:
            return await instance.handle_request(request=request)

        if handler.requires_loopback():
            handler_wrap = requires_loopback(handler_wrap)
        if handler.requires_auth():
            handler_wrap = requires_auth(handler_wrap)
        if handler.requires_api_key():
            handler_wrap = requires_api_key(handler_wrap)
        if handler.requires_csrf():
            handler_wrap = csrf_protect(handler_wrap)

        app.add_url_rule(
            f"{BASE_PATH}/{name}",
            f"{BASE_PATH}/{name}",
            handler_wrap,
            methods=handler.get_methods(),
        )

    # initialize and register API handlers
    handlers = load_classes_from_folder("python/api", "*.py", ApiHandler)
    for handler in handlers:
        register_api_handler(webapp, handler)

    # Adversys Added this: add the webapp, mcp, and a2a to the app
    middleware_routes = {
        f"{BASE_PATH}/mcp": ASGIMiddleware(app=mcp_server.DynamicMcpProxy.get_instance()),  # type: ignore
        f"{BASE_PATH}/a2a": ASGIMiddleware(app=fasta2a_server.DynamicA2AProxy.get_instance()),  # type: ignore
    }

    app = DispatcherMiddleware(webapp, middleware_routes)  # type: ignore

    PrintStyle().debug(f"Starting server at http://{host}:{port} ...")

    server = make_server(
        host=host,
        port=port,
        app=app,
        request_handler=NoRequestLoggingWSGIRequestHandler,
        threaded=True,
    )
    process.set_server(server)
    server.log_startup()

    # Start init_a0 in a background thread when server starts
    # This allows the server to start immediately while initialization happens in the background
    threading.Thread(target=init_a0, daemon=True).start()

    # run the server
    server.serve_forever()


def init_a0():
    # initialize contexts and MCP
    init_chats = initialize.initialize_chats()
    # only wait for init chats, otherwise they would seem to disappear for a while on restart
    init_chats.result_sync()

    initialize.initialize_mcp()
    # start job loop
    initialize.initialize_job_loop()
    # preload
    initialize.initialize_preload()



# run the internal server
if __name__ == "__main__":
    runtime.initialize()
    dotenv.load_dotenv()
    run()
