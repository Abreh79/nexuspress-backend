import unittest
from unittest.mock import patch, MagicMock
from nexuspress_ai.generators.article import ContentGenerator, ArticleDraft
from nexuspress_ai.publishers.wordpress import WordPressPublisher
from nexuspress_ai.core.config import Settings


class TestNexusPressCore(unittest.TestCase):

    def test_content_generator(self):
        generator = ContentGenerator()
        draft = generator.generate(topic="AI Agents", keywords=["ai", "agents"])
        self.assertIsInstance(draft, ArticleDraft)
        self.assertEqual(draft.title, "The Ultimate Guide to AI Agents")
        self.assertIn("ai", draft.keywords)
        self.assertIn("<h1>The Ultimate Guide to AI Agents</h1>", WordPressPublisher().convert_markdown_to_html(draft.body_markdown))
        self.assertIn("<img src=", WordPressPublisher().convert_markdown_to_html(draft.body_markdown))

    def test_wordpress_publisher_dry_run(self):
        generator = ContentGenerator()
        draft = generator.generate(topic="Headless CMS")
        publisher = WordPressPublisher(site_url="https://demo.wordpress.org")
        res = publisher.publish(draft)
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], "dry-run")
        self.assertIn("payload", res)

    @patch("httpx.Client")
    def test_wordpress_publisher_live_mock(self, mock_client_class):
        # Configure mock client behavior
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": 12345,
            "link": "https://demo.wordpress.org/headless-cms",
            "status": "draft"
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        generator = ContentGenerator()
        draft = generator.generate(topic="Headless CMS")
        
        publisher = WordPressPublisher(
            site_url="https://demo.wordpress.org",
            username="admin",
            app_password="secretpassword"
        )
        res = publisher.publish(draft)
        
        self.assertTrue(res["success"])
        self.assertEqual(res["mode"], "live")
        self.assertEqual(res["post_id"], 12345)
        self.assertEqual(res["link"], "https://demo.wordpress.org/headless-cms")


if __name__ == "__main__":
    unittest.main()
