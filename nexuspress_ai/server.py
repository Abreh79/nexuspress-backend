import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from generators.article import ContentGenerator


class NexusPressRequestHandler(BaseHTTPRequestHandler):
    """Local mock server representing the NexusPress Railway backend API."""

    def do_OPTIONS(self):
        """Handle browser preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_POST(self):
        # We only handle /api/v1/generate-ai
        if self.path == "/api/v1/generate-ai":
            self.handle_generate_ai()
        else:
            self.send_error_response(404, "Endpoint not found")

    def handle_generate_ai(self):
        # Verify headers
        auth_header = self.headers.get("Authorization", "")
        if not auth_header or not auth_header.startswith("Bearer "):
            self.send_error_response(401, "Missing or invalid Authorization header")
            return

        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            self.send_error_response(400, "Content-Type must be application/json")
            return

        # Read body content
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_error_response(400, "Empty request body")
            return

        body = self.rfile.read(content_length)
        try:
            payload = json.loads(body.decode("utf-8"))
            prompt = payload.get("prompt", "")

            # Generate content using generator
            generator = ContentGenerator()
            result = generator.generate(prompt)

            self.send_success_response({"status": "success", "data": result})
        except Exception as e:
            self.send_error_response(500, f"Internal generator error: {str(e)}")

    def send_success_response(self, payload: dict):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps(payload, indent=2).encode("utf-8"))

    def send_error_response(self, status_code: int, message: str):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}, indent=2).encode("utf-8"))
