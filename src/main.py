import argparse
import sys
from pathlib import Path

from src.gitignores import GitignoreManager
from src.workflows import WorkflowManager, Workflows


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scaffold new GitHub repositories with best practices"
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Init command
    init_parser = subparsers.add_parser("init", help="Initialize a new project")
    init_parser.add_argument("name", help="Name of the project")
    init_parser.add_argument(
        "--language", "-l", help="Programming language for .gitignore"
    )
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
        for type_name, workflows in available_workflows.items():
            print(f"  {type_name}: {', '.join(workflows)}")

        selected_types = []
        for workflow_type in Workflows:
            if input(f"Add {workflow_type.value} workflow? (y/N): ").lower() == "y":
                selected_types.append(workflow_type)

        if selected_types:
            created = workflow_manager.fetch_workflow(
                args.language, selected_types, project_path / ".github" / "workflows"
            )
            print(f"Created {len(created)} workflows")

    # README generation
    if not args.no_readme:
        ...

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
