# cli.py - simple CLI for ingest / summarize / render
import argparse
from cli_ingest import run_ingestion
from src.summarize.summarizer import Summarizer
from src.render.renderer import Renderer

def main():
    parser = argparse.ArgumentParser(prog="Agentic AI Digest")
    subparsers = parser.add_subparsers(dest="command")

    p_ingest = subparsers.add_parser("ingest", help="Fetch feeds and store articles")
    p_ingest.add_argument("--limit", type=int, default=2, help="(optional) per-feed limit when fetching")

    p_sum = subparsers.add_parser("summarize", help="Summarize new articles")
    p_sum.add_argument("--limit", type=int, default=5, help="Max articles to summarize")
    p_sum.add_argument("--category", type=str, help="Filter by category")
    p_sum.add_argument("--refresh", action="store_true", help="Reset existing summaries and regenerate")


    p_render = subparsers.add_parser("render", help="Render digest")
    p_render.add_argument("--limit", type=int, default=10, help="Max articles to include in digest")
    p_render.add_argument("--format", choices=["html","pdf","md"], default="pdf", help="Output format")
    p_render.add_argument("--category", type=str, help="Filter by category")

    p_clean = subparsers.add_parser("clean", help="Cleanup old or all articles from DB")
    p_clean.add_argument("--days", type=int, help="Delete articles older than N days")
    p_clean.add_argument("--all", action="store_true", help="Delete all articles (reset DB)")



    args = parser.parse_args()

    if args.command == "ingest":
        # run ingestion (cli_ingest uses its own limit inside - we keep it simple)
        run_ingestion(limit=args.limit)
    elif args.command == "summarize":
        from sqlite_utils import Database
        db = Database("data/cache/digest.db")
        if args.refresh and args.category:
            # reset summaries in this category
            for row in db["articles"].rows_where("category = :cat", {"cat": args.category}):
                db["articles"].update(row["id"], {"summary_brief": None, "summary_extended": None})
            print(f"🔄 Refreshed summaries for category: {args.category}")
        Summarizer().run(limit=args.limit, category=args.category)
        
    elif args.command == "render":
        renderer = Renderer()
        if args.format == "html":
            renderer.render_html("output.html", limit=args.limit,category=args.category)
        elif args.format == "md":
            renderer.render_md("digest.md", limit=args.limit, category=args.category)
        else:
            # Note: PDF requires GTK / WeasyPrint working on your system
            renderer.render_pdf("output.pdf", limit=args.limit,category=args.category)
    elif args.command == "clean":
        from sqlite_utils import Database
        import datetime, yaml, pathlib

        db = Database("data/cache/digest.db")
        config_file = pathlib.Path("configs/config.yaml")
        retention_days = None

        if config_file.exists():
            cfg = yaml.safe_load(config_file.read_text())
            retention_days = cfg.get("retention_days")

        if args.all:
            db["articles"].drop()
            print("🗑️ All articles deleted, DB reset.")
        elif args.days:
            cutoff = datetime.datetime.now() - datetime.timedelta(days=args.days)
            deleted = db["articles"].delete_where("published_at < :cutoff", {"cutoff": cutoff.isoformat()})
            print(f"🧹 Deleted {deleted} articles older than {args.days} days.")
        elif retention_days:
            cutoff = datetime.datetime.now() - datetime.timedelta(days=retention_days)
            deleted = db["articles"].delete_where("published_at < :cutoff", {"cutoff": cutoff.isoformat()})
            print(f"🧹 Deleted {deleted} articles older than {retention_days} days (from config).")
        else:
            print("⚠️ Use --days N, --all, or set retention_days in config.yaml")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
