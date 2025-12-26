from python.helpers.api import ApiHandler, Request, Response
from python.helpers.file_browser import FileBrowser
from python.helpers import runtime, files

class GetWorkDirFiles(ApiHandler):

    @classmethod
    def get_methods(cls):
        return ["GET"]

    async def process(self, input: dict, request: Request) -> dict | Response:
        current_path = request.args.get("path", "")
        # Normalize: strip whitespace and slashes
        if current_path:
            current_path = current_path.strip().strip("/")
        
        # Normalize special paths: "$WORK_DIR" or "root" (case-insensitive) mean empty path
        if current_path.upper() == "$WORK_DIR" or current_path.lower() == "root":
            # Default to empty path (will use base_dir from FileBrowser, which is /app)
            current_path = ""

        # browser = FileBrowser()
        # result = browser.get_files(current_path)
        result = await runtime.call_development_function(get_files, current_path)

        return {"data": result}


async def get_files(path):
    browser = FileBrowser()
    return browser.get_files(path)
