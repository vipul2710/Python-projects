import yaml
from pathlib import Path

def main():
    print("🚀 Agentic AI Digest — Pipeline Wired")

    # Load sources.yaml
    config_path = Path("configs/sources.yaml")
    if not config_path.exists():
        print("❌ sources.yaml not found!")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        sources = yaml.safe_load(f)

    # Print first 2 categories as a sanity check
    print("\nLoaded categories:")
    for i, (category, feeds) in enumerate(sources.items()):
        print(f"- {category}: {len(feeds)} sources")
        if i == 1:
            break

if __name__ == "__main__":
    main()
