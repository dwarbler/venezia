import argparse
import sys
from pathlib import Path

from src.gitignores import GitignoreManager
from src.readme import ReadmeGenerator
from src.workflows import WorkflowManager


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold new GitHub repositories with best practices"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Name of the project")
    init_parser.add_argument(
        "--language", "-l", help="Programming language for .gitignore"
    )
    parser.add_argument("--description", "-d", help="Project description")
    parser.add_argument("--author", help="Project author name")
    parser.add_argument("--github-username", help="GitHub username")
    init_parser.add_argument(
        "--path", "-p", type=Path, default=Path.cwd(), help="Project directory"
    )
    init_parser.add_argument(
        "--no-github-actions", action="store_true", help="Skip GitHub Actions setup"
    )
    init_parser.add_argument(
        "--no-readme", action="store_true", help="Skip README generation"
    )

    # List templates command
    list_parser = subparsers.add_parser("list", help="List available templates")

    return parser


def init_project(args):
    """Initialize a new project with the given arguments."""
    project_path = args.path / args.name
    project_path.mkdir(parents=True, exist_ok=True)

    print(f"Creating project in {project_path}")

    # Setup .gitignore
    gitignore = GitignoreManager()
    if args.language:
        try:
            gitignore.create_gitignore(args.language, project_path / ".gitignore")
            print(f"Created .gitignore for {args.language}")
        except Exception as e:
            print(f"Failed to create .gitignore: {e}", file=sys.stderr)
    else:
        # Show available templates and prompt user
        templates = gitignore.list_available_templates()
        print("\nAvailable templates:")
        for i, template in enumerate(templates, 1):
            print(f"{i}. {template}")

        while True:
            try:
                choice = input("\nSelect template number: ")
                template = templates[int(choice) - 1]
                gitignore.create_gitignore(template, project_path / ".gitignore")
                print(f"Created .gitignore for {template}")
                break
            except (ValueError, IndexError):
                print("Invalid selection, try again")

    # GitHub Actions setup
    if not args.no_github_actions:
        workflow_manager = WorkflowManager()

        # Let user select workflow types
        available_workflows = workflow_manager.list_language_workflows(args.language)
        print("\nAvailable workflow types:")
        for workflow in available_workflows:
            print(f" -- {workflow.name}")

        selected_types = []
        for workflow_type in available_workflows:
            if input(f"Add {workflow_type.stem} workflow? (y/N): ").lower() == "y":
                selected_types.append(workflow_type.stem)

        if selected_types:
            created = workflow_manager.fetch_workflow(
                args.language, selected_types, project_path / ".github" / "workflows"
            )
            print(f"Created {len(created)} workflows")

    # README generation
    if not args.no_readme:
        readme_gen = ReadmeGenerator()

        # Get project description if not provided
        description = args.description
        if not description:
            description = input("Enter project description: ")

        # Additional variables for README template
        variables = {
            "author": args.author or input("Enter author name: "),
            "github_username": args.github_username or input("Enter GitHub username: "),
        }

        try:
            readme_path = readme_gen.fetch_readme(
                project_name=args.name,
                language=args.language,
                description=description,
                variables=variables,
                output_path=project_path / "README.md",
            )
            print(f"✓ Created README at {readme_path}")
        except Exception as e:
            print(f"✗ Failed to create README: {e}", file=sys.stderr)

    print(f"\nProject {args.name} created successfully!")
    print("\nNext steps:")
    print(f"1. cd {project_path}")
    print("2. Initialize your dependencies")
    print("3. Make your first commit")


def list_templates():
    """List all available gitignore templates."""
    gitignore = GitignoreManager()
    templates = gitignore.list_available_templates()

    print("Available templates:")
    for template in templates:
        print(f"  • {template}")


def main():
    parser = create_parser()
    args = parser.parse_args()

    if args.command == "init":
        init_project(args)
    elif args.command == "list":
        list_templates()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
