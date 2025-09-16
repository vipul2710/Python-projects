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

    p_render = subparsers.add_parser("render", help="Render digest")
    p_render.add_argument("--limit", type=int, default=10, help="Max articles to include in digest")
    p_render.add_argument("--format", choices=["html","pdf"], default="html", help="Output format")

    args = parser.parse_args()

    if args.command == "ingest":
        # run ingestion (cli_ingest uses its own limit inside - we keep it simple)
        run_ingestion(limit=args.limit)
    elif args.command == "summarize":
        Summarizer().run(limit=args.limit)
    elif args.command == "render":
        renderer = Renderer()
        if args.format == "html":
            renderer.render_html("output.html", limit=args.limit)
        else:
            # Note: PDF requires GTK / WeasyPrint working on your system
            renderer.render_pdf("output.pdf", limit=args.limit)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
