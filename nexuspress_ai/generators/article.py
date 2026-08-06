from typing import List, Optional
from pydantic import BaseModel, Field
from nexuspress_ai.core.config import settings as global_settings


class ArticleDraft(BaseModel):
    title: str
    slug: str
    summary: str
    body_markdown: str
    keywords: List[str] = Field(default_factory=list)
    meta_description: Optional[str] = None
    status: str = "draft"
    featured_image_url: Optional[str] = None


class ContentGenerator:
    """Generates structured article drafts from topics and parameters."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or global_settings.default_model

    def generate(self, topic: str, keywords: Optional[List[str]] = None) -> ArticleDraft:
        kw_list = keywords or ["AI Publishing", "NexusPress AI", "SEO"]
        kw_str = ", ".join(kw_list)
        slug = topic.lower().replace(" ", "-").replace("/", "-")
        
        title = f"The Ultimate Guide to {topic}"
        summary = f"Learn how {topic} is transforming modern digital publishing with advanced workflows and keyword strategies targeting {kw_str}."
        
        # Build structured rich markdown with H2, H3, and image tags
        body = f"""# {title}

![{topic} Feature Image](https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80)

## Introduction
Digital landscape changes quickly. In this comprehensive guide, we will dive deep into **{topic}** and explore its core implications. Incorporating high-intent search terms like *{kw_str}* is essential for modern search engine visibility.

## Understanding the Foundations of {topic}
To master {topic}, one must first understand its foundational pillars. Here, we outline the primary mechanics and concepts.

### High-Performance Pipelines
Implementing structured workflows yields consistent, robust output. By leveraging programmatic generation, content teams can achieve unprecedented scale without sacrificing quality.

### SEO-First Optimization
Integrating relevant terms such as **{kw_list[0]}** directly within heading hierarchies and body prose allows crawlers to properly index and attribute value to the content.

## Implementation Guide
Follow these steps to deploy {topic} into production environments:

### Step 1: Planning and Scaffolding
Establish your workspace, define your core taxonomies, and layout initial content clusters.

### Step 2: Content Generation & Review
Draft rich-text articles while ensuring that semantic density remains high.

![Workflow Optimization Diagram](https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&w=800&q=80)

### Step 3: Deployment and Publishing
Utilize standard REST APIs or headless content hubs to deliver compiled assets.

## Conclusion and Future Trends
As we look to the future, **{topic}** will undoubtedly remain at the center of innovation. Staying ahead requires a dedicated focus on automation and quality metrics.
"""
        return ArticleDraft(
            title=title,
            slug=slug,
            summary=summary,
            body_markdown=body,
            keywords=kw_list,
            meta_description=summary[:150],
            featured_image_url="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=1200&q=80"
        )
