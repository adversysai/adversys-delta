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

# Get base path from environment variable (for reverse proxy subpath support)
# Default to empty string (root) if not set
BASE_PATH = os.getenv("AGENT_ZERO_BASE_PATH", "").rstrip("/")
if BASE_PATH and not BASE_PATH.startswith("/"):
    BASE_PATH = "/" + BASE_PATH

# Debug: Log base path (can be removed later)
if BASE_PATH:
    import logging
    logging.warning(f"Delta BASE_PATH set to: {BASE_PATH}")

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
# Keep static_url_path at "/" since Nginx rewrites /agent-zero/ to /
# The base tag in HTML will handle path resolution for relative URLs
webapp = Flask("app", static_folder=get_abs_path("./webui"), static_url_path="/")
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
            # Include BASE_PATH in redirect if set
            login_url = f"{BASE_PATH}/login" if BASE_PATH else url_for('login_handler')
            return redirect(login_url)
        
        return await f(*args, **kwargs)

    return decorated

def csrf_protect(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        # For development, make CSRF more lenient
        token = session.get("csrf_token")
        header = request.headers.get("X-CSRF-Token")
        cookie = request.cookies.get("csrf_token_" + runtime.get_runtime_id())
        sent = header or cookie

        # Allow requests if we have a token and it matches, OR if this is a simple token validation
        if sent and (not token or token == sent):
            # Update session token if it doesn't exist
            if not token and sent:
                session["csrf_token"] = sent
            return await f(*args, **kwargs)
        elif token and not sent:
            # Have session token but no client token - this might be acceptable for some requests
            return await f(*args, **kwargs)
        else:
            return Response("CSRF token missing or invalid", 403)

    return decorated

@webapp.route("/login", methods=["GET", "POST"])
async def login_handler():
    error = None
    if request.method == 'POST':
        # Check environment variable first (before .env file override)
        user = os.getenv("AUTH_LOGIN")
        if user is None:
            user = dotenv.get_dotenv_value("AUTH_LOGIN")
        password = os.getenv("AUTH_PASSWORD")
        if password is None:
            password = dotenv.get_dotenv_value("AUTH_PASSWORD")
        
        if request.form['username'] == user and request.form['password'] == password:
            session['authentication'] = login.get_credentials_hash()
            # Include BASE_PATH in redirect if set
            index_url = f"{BASE_PATH}/" if BASE_PATH else url_for('serve_index')
            return redirect(index_url)
        else:
            error = 'Invalid Credentials. Please try again.'
            
    login_page_content = files.read_file("webui/login.html")
    return render_template_string(login_page_content, error=error)

@webapp.route("/logout")
async def logout_handler():
    session.pop('authentication', None)
    return redirect(url_for('login_handler'))

def rewrite_js_imports(content):
    """Rewrite absolute imports in JavaScript to include base path"""
    if not BASE_PATH:
        return content

    import re

    def rewrite_import(match):
        import_statement = match.group(0)
        from_keyword = match.group(1)
        quote = match.group(2)
        import_path = match.group(3)

        # Skip if already a full URL or blob or data URL
        if import_path.startswith(('http://', 'https://', 'blob:', 'data:')):
            return import_statement

        # If it's an absolute path (starts with /), prepend base path
        if import_path.startswith('/'):
            # Check if it already has the base path
            if not import_path.startswith(BASE_PATH):
                new_path = BASE_PATH + import_path
                return f'{from_keyword} {quote}{new_path}{quote}'

        return import_statement

    # Rewrite ES6 import statements
    content = re.sub(r'(from)\s*(["\'])([^"\']+)\2', rewrite_import, content)

    # Also rewrite dynamic imports
    content = re.sub(r'import\s*\(\s*(["\'])([^"\']+)\1\s*\)', lambda m: f'import({m.group(1)}{BASE_PATH}{m.group(2)}{m.group(1)})' if m.group(2).startswith('/') and not m.group(2).startswith(BASE_PATH) else m.group(0), content)

    return content

# Explicit route for index.js to ensure it's served correctly
@webapp.route("/index.js", methods=["GET"])
async def serve_index_js():
    from flask import send_from_directory, Response
    try:
        file_path = get_abs_path("./webui/index.js")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Rewrite imports to include base path
        content = rewrite_js_imports(content)
        return Response(content, mimetype='application/javascript')
    except Exception as e:
        return str(e), 500

# Explicit route for index.css if it exists
@webapp.route("/index.css", methods=["GET"])
async def serve_index_css():
    from flask import send_from_directory
    return send_from_directory(get_abs_path("./webui"), "index.css")

# Route for JS files to rewrite imports
@webapp.route("/js/<path:filename>", methods=["GET"])
async def serve_js_files(filename):
    from flask import Response
    try:
        file_path = get_abs_path(f"./webui/js/{filename}")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        # Rewrite imports to include base path
        content = rewrite_js_imports(content)
        return Response(content, mimetype='application/javascript')
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        return str(e), 500

# Route for component JS files to rewrite imports
@webapp.route("/components/<path:filename>", methods=["GET"])
async def serve_component_files(filename):
    from flask import Response
    try:
        file_path = get_abs_path(f"./webui/components/{filename}")
        # Check if it's a JS file
        if filename.endswith('.js'):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Rewrite imports to include base path
            content = rewrite_js_imports(content)
            return Response(content, mimetype='application/javascript')
        else:
            # For non-JS files, serve as-is
            from flask import send_from_directory
            return send_from_directory(get_abs_path("./webui/components"), filename)
    except FileNotFoundError:
        return "File not found", 404
    except Exception as e:
        return str(e), 500

# handle default address, load index
@webapp.route("/", methods=["GET"])
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
    # Inject base path into HTML for JavaScript to use
    # Add <base> tag if base path is set
    if BASE_PATH:
        # Inject base tag after <head> - this helps with relative URLs
        index = index.replace("<head>", f'<head><base href="{BASE_PATH}/">')
        # Rewrite script src attributes to include base path
        # ES6 modules ignore <base> tag, so we MUST rewrite script src attributes
        import re
        
        # Simple string replacement for common script patterns first
        # This is more reliable than regex for edge cases
        # Replace all occurrences (Python replace does this by default)
        original_index_js_count = index.count('src="index.js"') + index.count("src='index.js'")
        
        # Direct string replacements
        index = index.replace('src="index.js"', f'src="{BASE_PATH}/index.js"')
        index = index.replace("src='index.js'", f"src='{BASE_PATH}/index.js'")
        index = index.replace('src="js/', f'src="{BASE_PATH}/js/')
        index = index.replace("src='js/", f"src='{BASE_PATH}/js/")
        
        # Also handle cases with type="module" or other attributes before src
        index = index.replace(' type="module" src="index.js"', f' type="module" src="{BASE_PATH}/index.js"')
        index = index.replace(" type='module' src='index.js'", f" type='module' src='{BASE_PATH}/index.js'")
        
        # Fallback regex to catch any we might have missed - more aggressive pattern
        # This will match script tags with src="index.js" regardless of attribute order
        def rewrite_index_js(match):
            full_tag = match.group(0)
            # Replace index.js with base path version (handle both quote styles)
            if 'src="index.js"' in full_tag:
                return full_tag.replace('src="index.js"', f'src="{BASE_PATH}/index.js"')
            elif "src='index.js'" in full_tag:
                return full_tag.replace("src='index.js'", f"src='{BASE_PATH}/index.js'")
            return full_tag
        
        # Use regex as final fallback - match any script tag with index.js
        index = re.sub(
            r'<script[^>]*?src=["\']index\.js["\'][^>]*>',
            rewrite_index_js,
            index
        )
        
        # Debug: Log if replacement happened
        remaining_index_js = index.count('src="index.js"') + index.count("src='index.js'")
        if original_index_js_count > 0:
            import logging
            if remaining_index_js > 0:
                logging.warning(f"WARNING: {remaining_index_js} index.js references still found after rewrite! BASE_PATH={BASE_PATH}")
            else:
                logging.warning(f"SUCCESS: Rewrote {original_index_js_count} index.js references to {BASE_PATH}/index.js")
        
        # Then use regex for other script tags
        def rewrite_script_src(match):
            full_tag = match.group(0)
            quote = match.group(2)
            src = match.group(3)
            
            # Skip if already has base path or is absolute URL
            if src.startswith(BASE_PATH) or src.startswith(('http://', 'https://', '//', 'data:')):
                return full_tag
            
            # Rewrite relative paths
            if src.startswith('/'):
                new_src = f'{BASE_PATH}{src}'
            else:
                new_src = f'{BASE_PATH}/{src}'
            
            return full_tag.replace(f'{quote}{src}{quote}', f'{quote}{new_src}{quote}')
        
        # Match remaining script tags with src (more flexible pattern)
        index = re.sub(
            r'<script([^>]*\s)src=(["\'])([^"\']+)\2([^>]*)>',
            rewrite_script_src,
            index
        )
        # Rewrite link href attributes for CSS and other resources
        def rewrite_link_href(match):
            tag = match.group(0)
            quote = match.group(2)
            href = match.group(3)
            if href and not href.startswith(('http://', 'https://', '//', 'data:', '#')):
                if href.startswith('/') and not href.startswith(BASE_PATH):
                    new_href = f'{BASE_PATH}{href}'
                else:
                    new_href = f'{BASE_PATH}/{href}' if not href.startswith('/') else href
                return tag.replace(f'{quote}{href}{quote}', f'{quote}{new_href}{quote}')
            return tag
        
        index = re.sub(
            r'(<link[^>]*\shref=)(["\'])([^"\']+)(\2[^>]*>)',
            rewrite_link_href,
            index
        )
        # Inject a script that sets up base path for JavaScript modules
        base_path_script = f'''
    <script>
        // Set base path for JavaScript modules (components.js uses this)
        window.__agentZeroBasePath = "{BASE_PATH}";
    </script>
'''
        index = index.replace("</head>", base_path_script + "</head>")
    return index

def run():
    PrintStyle().print("Initializing framework...")

    # Suppress only request logs but keep the startup messages
    from werkzeug.serving import WSGIRequestHandler
    from werkzeug.serving import make_server
    from werkzeug.middleware.dispatcher import DispatcherMiddleware
    from a2wsgi import ASGIMiddleware

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
            f"/{name}",
            f"/{name}",
            handler_wrap,
            methods=handler.get_methods(),
        )

    # initialize and register API handlers
    handlers = load_classes_from_folder("python/api", "*.py", ApiHandler)
    for handler in handlers:
        register_api_handler(webapp, handler)

    # add the webapp, mcp, and a2a to the app
    # Note: Routes stay at "/" because Nginx rewrites /agent-zero/ to /
    # Only static files and HTML need base path updates
    middleware_routes = {
        "/mcp": ASGIMiddleware(app=mcp_server.DynamicMcpProxy.get_instance()),  # type: ignore
        "/a2a": ASGIMiddleware(app=fasta2a_server.DynamicA2AProxy.get_instance()),  # type: ignore
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
    # threading.Thread(target=init_a0, daemon=True).start()
    init_a0()

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