import threading
import time
import unittest
import httpx
from http.server import HTTPServer
from nexuspress_ai.server import NexusPressRequestHandler


class TestNexusPressServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Setup mock server running in a background thread
        cls.port = 8888
        cls.server = HTTPServer(("127.0.0.1", cls.port), NexusPressRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        # Give the server a moment to bind and start
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_endpoint_not_found(self):
        url = f"http://127.0.0.1:{self.port}/invalid-endpoint"
        response = httpx.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())

    def test_missing_auth(self):
        url = f"http://127.0.0.1:{self.port}/api/v1/generate-ai"
        response = httpx.post(url, json={"title": "Test Topic"})
        self.assertEqual(response.status_code, 401)
        self.assertIn("Authorization", response.json()["error"])

    def test_missing_content_type(self):
        url = f"http://127.0.0.1:{self.port}/api/v1/generate-ai"
        headers = {"Authorization": "Bearer test-key"}
        response = httpx.post(url, headers=headers, content="Plain Text Payload")
        self.assertEqual(response.status_code, 400)

    def test_successful_seo_generation(self):
        url = f"http://127.0.0.1:{self.port}/api/v1/generate-ai"
        headers = {
            "Authorization": "Bearer my-secret-license-key",
            "Content-Type": "application/json"
        }
        payload = {
            "title": "WordPress Automation",
            "content": "This is a quick summary about automatic pipelines"
        }
        response = httpx.post(url, headers=headers, json=payload, timeout=5.0)
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("seo_title", data)
        self.assertIn("meta_description", data)
        self.assertIn("focus_keywords", data)
        self.assertIn("draft", data)
        self.assertEqual(data["draft"]["title"], "The Ultimate Guide to WordPress Automation")


if __name__ == "__main__":
    unittest.main()
