import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from nexuspress_ai.generators.article import ContentGenerator


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
            self.send_error_response(401, "Missing or invalid Authorization license key")
            return

        content_type = self.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            self.send_error_response(400, "Content-Type must be application/json")
            return

        # Read body content
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            self.send_error_response(400, "Request body is empty")
            return

        try:
            body_bytes = self.rfile.read(content_length)
            data = json.loads(body_bytes.decode("utf-8"))
        except Exception as e:
            self.send_error_response(400, f"Invalid JSON payload: {str(e)}")
            return

        title = data.get("title")
        content_snippet = data.get("content", "")

        if not title:
            self.send_error_response(422, "Missing required parameter 'title'")
            return

        # Generate the SEO suggestions using the Python Engine
        try:
            generator = ContentGenerator()
            draft = generator.generate(topic=title)
            
            # Formulate response payload matching what the WordPress client expects
            response_payload = {
                "success": True,
                "seo_title": f"{draft.title} | SEO Optimized",
                "meta_description": draft.meta_description,
                "focus_keywords": draft.keywords,
                "readability_score": 92,
                "suggested_headings": [
                    "Introduction",
                    f"Foundations of {title}",
                    "Implementation Guide",
                    "Conclusion"
                ],
                "draft": {
                    "title": draft.title,
                    "slug": draft.slug,
                    "body": draft.body_markdown,
                    "excerpt": draft.summary
                }
            }
            
            self.send_success_response(response_payload)

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
import os
from socketserver import ThreadingMixIn

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True

def run_server():
    port = int(os.environ.get("PORT", 8000))
    server_address = ("0.0.0.0", port)
    httpd = ThreadedHTTPServer(server_address, NexusPressRequestHandler)
    print(f"NexusPress backend running on port {port} (threaded)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server...")

if __name__ == "__main__":
    run_server()
