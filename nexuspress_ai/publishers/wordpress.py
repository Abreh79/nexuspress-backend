import httpx
from typing import Dict, Any, Optional
from nexuspress_ai.generators.article import ArticleDraft
from nexuspress_ai.core.config import Settings, settings as global_settings


class WordPressPublisher:
    """Handles publishing content to WordPress via WP REST API."""

    def __init__(
        self,
        site_url: Optional[str] = None,
        username: Optional[str] = None,
        app_password: Optional[str] = None,
        config: Optional[Settings] = None
    ):
        cfg = config or global_settings
        self.site_url = (site_url or cfg.wordpress_url or "https://example.com").rstrip("/")
        self.username = username or cfg.wordpress_user or ""
        self.app_password = app_password or cfg.wordpress_app_password or ""

    def convert_markdown_to_html(self, markdown_text: str) -> str:
        """Simple lightweight markdown to HTML converter for WordPress compatibility."""
        lines = markdown_text.split("\n")
        html_lines = []
        in_list = False
        
        for line in lines:
            line_str = line.strip()
            
            # Unordered lists
            if line_str.startswith("- ") or line_str.startswith("* "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                item = line_str[2:]
                html_lines.append(f"<li>{item}</li>")
                continue
            elif in_list:
                html_lines.append("</ul>")
                in_list = False
                
            # Headings
            if line_str.startswith("# "):
                html_lines.append(f"<h1>{line_str[2:]}</h1>")
            elif line_str.startswith("## "):
                html_lines.append(f"<h2>{line_str[3:]}</h2>")
            elif line_str.startswith("### "):
                html_lines.append(f"<h3>{line_str[4:]}</h3>")
            # Images
            elif line_str.startswith("![") and "]" in line_str and "(" in line_str:
                alt_start = 2
                alt_end = line_str.find("]")
                url_start = line_str.find("(") + 1
                url_end = line_str.find(")")
                alt = line_str[alt_start:alt_end]
                url = line_str[url_start:url_end]
                html_lines.append(f'<img src="{url}" alt="{alt}" style="max-width:100%; height:auto;" />')
            # Empty lines
            elif not line_str:
                html_lines.append("<br />")
            # Normal paragraphs
            else:
                # Basic strong formatting
                processed = line_str
                while "**" in processed:
                    processed = processed.replace("**", "<strong>", 1).replace("**", "</strong>", 1)
                while "*" in processed:
                    processed = processed.replace("*", "<em>", 1).replace("*", "</em>", 1)
                html_lines.append(f"<p>{processed}</p>")
                
        if in_list:
            html_lines.append("</ul>")
            
        return "\n".join(html_lines)

    def prepare_payload(self, draft: ArticleDraft) -> Dict[str, Any]:
        html_content = self.convert_markdown_to_html(draft.body_markdown)
        return {
            "title": draft.title,
            "slug": draft.slug,
            "content": html_content,
            "excerpt": draft.summary,
            "status": "draft" if draft.status == "draft" else "publish",
        }

    def publish(self, draft: ArticleDraft) -> Dict[str, Any]:
        payload = self.prepare_payload(draft)
        
        if not self.site_url:
            return {
                "success": False,
                "error": "No WordPress site URL configured or provided.",
                "payload": payload
            }

        endpoint = f"{self.site_url}/wp-json/wp/v2/posts"
        
        # If no auth credentials, perform a dry-run draft return
        if not self.username or not self.app_password:
            return {
                "success": True,
                "mode": "dry-run",
                "message": f"Dry-run: Credentials missing. Payload prepared for {endpoint}.",
                "payload": payload
            }

        try:
            # Send HTTP POST request with standard HTTP Basic Auth (recommended for WP App Passwords)
            with httpx.Client(timeout=15.0) as client:
                response = client.post(
                    endpoint,
                    json=payload,
                    auth=(self.username, self.app_password)
                )
                
            if response.status_code in (200, 201):
                res_data = response.json()
                return {
                    "success": True,
                    "mode": "live",
                    "post_id": res_data.get("id"),
                    "link": res_data.get("link"),
                    "status": res_data.get("status"),
                    "message": f"Successfully published post '{draft.title}' (ID: {res_data.get('id')})"
                }
            else:
                return {
                    "success": False,
                    "error": f"WordPress REST API error ({response.status_code}): {response.text}",
                    "payload": payload
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to connect to WordPress site: {str(e)}",
                "payload": payload
            }
