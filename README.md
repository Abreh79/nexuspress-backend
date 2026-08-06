# NexusPress AI

NexusPress AI is an autonomous, AI-driven content generation, SEO optimization, and multi-platform publishing engine.

## Features
- **AI Content Generation**: Structured article drafting, SEO keyword targeting, and tone styling.
- **Multi-CMS Publisher**: REST API integrations for WordPress, headless CMS, and custom webhooks.
- **Workflow Pipeline**: Automated pipeline taking raw ideas -> outline -> draft -> SEO audit -> publish/schedule.
- **CLI Interface**: Powerful command-line tool for local execution and cron automation.

## Quick Start

### Installation
```bash
pip install -e .
```

### Usage
```bash
# Generate a draft
nexuspress generate --topic "The Future of Autonomous AI Agents" --output draft.json

# Publish to CMS
nexuspress publish --draft draft.json --target wordpress
```
