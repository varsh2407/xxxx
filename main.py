#!/usr/bin/env python3
"""
VibeCoding CLI — Transform any idea into a production-ready enterprise application.

Usage:
    python main.py "Build a weather app with user accounts and saved locations"
    python main.py "Build a task management SaaS" --output ./my_app --skip security qa
    python main.py --interactive
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables FIRST before any imports that need them
load_dotenv()

from orchestrator import VibeCodingOrchestrator


def setup_logging(verbose: bool = False) -> None:
    """Configure structured logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("vibecoding.log"),
        ],
    )
    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)


def validate_environment() -> list[str]:
    """Check required environment variables are set."""
    required = ["AZURE_API_KEY", "AZURE_API_BASE", "AZURE_DEPLOYMENT"]
    missing = [var for var in required if not os.getenv(var)]
    return missing


def interactive_mode() -> tuple[str, str, list, bool, bool]:
    """Run interactive prompt collection."""
    print("\n🚀 VibeCoding Interactive Mode")
    print("─" * 40)

    while True:
        prompt = input("\n💬 Describe your application idea:\n> ").strip()
        if len(prompt) < 10:
            print("⚠  Please provide a more detailed description (at least 10 characters).")
            continue
        break

    output_dir = input("\n📁 Output directory [./generated_app]: ").strip()
    output_dir = output_dir or "./generated_app"

    print("\n⏭  Skip phases? (faster build, fewer features)")
    print("   Options: frontend, devops, security, qa")
    skip_input = input("   Enter phases to skip (comma-separated, or press Enter for full build): ").strip()
    skip_phases = [s.strip() for s in skip_input.split(",") if s.strip()] if skip_input else []

    github = input("\n🐙 Push to GitHub? [y/N]: ").strip().lower() == "y"
    github_private = False
    if github:
        github_private = input("   Make repo private? [y/N]: ").strip().lower() == "y"

    return prompt, output_dir, skip_phases, github, github_private


def main():
    parser = argparse.ArgumentParser(
        description="VibeCoding: Enterprise Application Generator from Natural Language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py "Build a weather app with user auth and saved locations"
  python main.py "Build a multi-tenant SaaS invoicing platform" --output ./invoicer
  python main.py "Build an e-commerce API with product catalog and orders" --skip frontend
  python main.py --interactive
        """
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Natural language description of the application to build"
    )
    parser.add_argument(
        "--output", "-o",
        default="./generated_app",
        help="Output directory for generated code (default: ./generated_app)"
    )
    parser.add_argument(
        "--skip",
        nargs="*",
        choices=["frontend", "devops", "security", "qa"],
        default=[],
        help="Phases to skip for faster builds"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose/debug logging"
    )
    parser.add_argument(
        "--github",
        action="store_true",
        help="Push generated code to a new GitHub repository"
    )
    parser.add_argument(
        "--github-private",
        action="store_true",
        help="Make the GitHub repository private (default: public)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output directory without prompting"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Validate environment
    missing_vars = validate_environment()
    if missing_vars:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\nPlease set these in your .env file:")
        print(f"   AZURE_API_KEY=your_azure_openai_api_key")
        print(f"   AZURE_API_BASE=https://your-resource.openai.azure.com/")
        print(f"   AZURE_API_VERSION=2024-02-01")
        print(f"   AZURE_DEPLOYMENT=gpt-4o")
        sys.exit(1)

    # Collect inputs
    if args.interactive:
        prompt, output_dir, skip_phases, publish_github, github_private = interactive_mode()
    elif args.prompt:
        prompt = args.prompt
        output_dir = args.output
        skip_phases = args.skip or []
        publish_github = args.github
        github_private = args.github_private
    else:
        parser.print_help()
        sys.exit(1)

    # Validate GitHub env vars if publishing
    if publish_github:
        missing_gh = [v for v in ["GITHUB_TOKEN", "GITHUB_USERNAME"] if not os.getenv(v)]
        if missing_gh:
            print(f"\n❌ GitHub publishing requires these env vars:")
            for v in missing_gh:
                print(f"   - {v}")
            print("\nAdd them to your .env file and try again.")
            print("Create a token at: https://github.com/settings/tokens/new (scope: repo, workflow)")
            sys.exit(1)

    # Check output directory
    output_path = Path(output_dir)
    if output_path.exists() and not args.overwrite:
        response = input(f"\n⚠  Directory '{output_dir}' already exists. Overwrite? [y/N]: ").strip().lower()
        if response != "y":
            print("Aborted.")
            sys.exit(0)

    output_path.mkdir(parents=True, exist_ok=True)

    # Run the build
    try:
        orchestrator = VibeCodingOrchestrator()
        state = orchestrator.build_from_vibe(
            vibe_prompt=prompt,
            output_dir=str(output_path),
            skip_phases=skip_phases,
            publish_to_github=publish_github,
            github_private=github_private,
        )

        if state.status == "failed":
            print(f"\n❌ Build failed. Check vibecoding.log for details.")
            sys.exit(1)

        print(f"\n✅ Build successful! Your app is at: {output_path.absolute()}")

    except KeyboardInterrupt:
        print("\n\n⚠  Build interrupted by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Unexpected error: {e}")
        print("Check vibecoding.log for full details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
