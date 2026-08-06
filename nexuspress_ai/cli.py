import argparse
import json
import os
import sys
from nexuspress_ai.core.config import Settings
from nexuspress_ai.generators.article import ContentGenerator, ArticleDraft
from nexuspress_ai.publishers.wordpress import WordPressPublisher


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nexuspress",
        description="NexusPress AI - Autonomous AI Content & Publishing Engine"
    )
    
    # Global flag for .env file location
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to environment configuration file (default: .env)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Subcommand: generate
    gen_parser = subparsers.add_parser("generate", help="Generate an article draft")
    gen_parser.add_argument("--topic", "-t", required=True, help="Topic for the article")
    gen_parser.add_argument("--keywords", "-k", help="Comma-separated list of keywords")
    gen_parser.add_argument("--model", "-m", help="AI model to use (overrides config)")
    gen_parser.add_argument("--output", "-o", help="Save output JSON file path")

    # Subcommand: publish
    pub_parser = subparsers.add_parser("publish", help="Publish a draft to WordPress / CMS")
    pub_parser.add_argument("--draft", "-d", "--file", "-f", dest="draft", required=True, help="Path to draft JSON file")
    pub_parser.add_argument("--url", "--wp-url", help="WordPress site base URL")
    pub_parser.add_argument("--user", "--wp-user", help="WordPress username")
    pub_parser.add_argument("--password", "--wp-app-password", help="WordPress Application Password")
    pub_parser.add_argument("--dry-run", action="store_true", help="Force dry-run publishing output")

    # Subcommand: serve
    serve_parser = subparsers.add_parser("serve", help="Run local mock backend server for WP Plugin testing")
    serve_parser.add_argument("--port", type=int, default=8000, help="Port to run server on (default: 8000)")

    # Subcommand: config
    subparsers.add_parser("config", help="Inspect active configuration settings")

    return parser


def main(args_list=None):
    parser = create_parser()
    args = parser.parse_args(args_list)

    # Load configuration
    cfg = Settings.from_env(env_file=args.env_file)

    if args.command == "generate":
        kw_list = [k.strip() for k in args.keywords.split(",")] if args.keywords else []
        model_name = args.model or cfg.default_model
        generator = ContentGenerator(model_name=model_name)
        draft = generator.generate(topic=args.topic, keywords=kw_list)
        out_data = draft.model_dump_json(indent=2)

        if args.output:
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out_data)
            print(f"Draft successfully generated using model [{model_name}] and saved to {args.output}")
        else:
            print(out_data)

    elif args.command == "publish":
        if not os.path.exists(args.draft):
            print(f"Error: Draft file not found at path '{args.draft}'", file=sys.stderr)
            sys.exit(1)

        with open(args.draft, "r", encoding="utf-8") as f:
            data = json.load(f)

        draft = ArticleDraft(**data)
        
        # Override config credentials with explicit CLI flags if provided
        wp_url = args.url or cfg.wordpress_url
        wp_user = args.user or cfg.wordpress_user
        wp_pwd = args.password or cfg.wordpress_app_password

        # Handle dry-run flag
        if args.dry_run:
            publisher = WordPressPublisher(
                site_url=wp_url,
                username=None,  # Passing None guarantees a dry-run in publisher logic
                app_password=None,
                config=cfg
            )
        else:
            publisher = WordPressPublisher(
                site_url=wp_url,
                username=wp_user,
                app_password=wp_pwd,
                config=cfg
            )
            
        res = publisher.publish(draft)
        
        # If forced dry-run by flag, mark the response as mode "dry-run"
        if args.dry_run:
            res["mode"] = "dry-run"
            res["message"] = f"Forced dry-run: {res.get('message', '')}"
            
        print(json.dumps(res, indent=2))

    elif args.command == "serve":
        from nexuspress_ai.server import run_server
        run_server(port=args.port)

    elif args.command == "config":
        def redact(val):
            return "******" if val else "not set"

        print(json.dumps({
            "environment": cfg.environment,
            "default_model": cfg.default_model,
            "openai_api_key": redact(cfg.openai_api_key),
            "wordpress_url": cfg.wordpress_url or "not set",
            "wordpress_user": cfg.wordpress_user or "not set",
            "wordpress_app_password": redact(cfg.wordpress_app_password)
        }, indent=2))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
