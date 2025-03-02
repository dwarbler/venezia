from enum import Enum
from pathlib import Path
from typing import List

import yaml


class Workflows(Enum):
    TEST = "test"
    LINT = "lint"
    BUILD = "build"
    DEPLOY = "deploy"
    RELEASE = "release"
    DOCS = "docs"
    SECURITY = "security"


class Language(Enum):
    PYTHON = "python"
    RUST = "rust"
    TYPESCRIPT = "typescript"


class WorkflowManager:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates" / "workflows"

    def list_workflows(self) -> List[str]:
        """List all available workflows.

        Returns:
            List[str]: the list of workflow names
        """
        return [f.stem for f in self.template_dir.iterdir() if f.is_dir()]

    def list_language_workflows(self, language: Language):
        """List all available workflows for a specific language.

        Args:
            language (Languages): the language to list workflows for

        Returns:
            dict[str, list[str]]: workflows of the passed language
        """
        workflows = {}
        workflow_dir = self.template_dir / language.value

        if not workflow_dir.exists():
            raise ValueError(f"No workflows found for {language}")

        for workflow in workflow_dir.iterdir():
            files = list(workflow_dir.glob(f"{workflow.name}/*.yml"))
            if files:
                workflows[workflow.name] = [f.stem for f in files]

        return workflows

    def fetch_workflow(
        self,
        language: str,
        types: List[Workflows],
        output_path: Path = Path(".github/workflows"),
    ):
        """Generate a new workflow file in the repository.

        Args:
            name (str): the name of the workflow
            language (str): the language of the workflow
            output_path (Path, optional): the path to the output directory. Defaults to Path(".github/workflows").
        """
        output_path.mkdir(parents=True, exist_ok=True)
        created_files = []

        lang_dir = self.template_dir / language
        if not lang_dir.exists():
            raise ValueError(f"No workflows found for {language}")

        for workflow_type in types:
            template_path = lang_dir / f"{workflow_type.value}.yml"
            if not template_path.exists():
                print(
                    f"Warning: No {workflow_type.value} workflow found for {language}"
                )
                continue

            output_file = output_path / f"{language}-{workflow_type.value}.yml"
            with template_path.open() as f:
                template = yaml.safe_load(f)

            with output_file.open("w") as f:
                yaml.safe_dump(template, f, sort_keys=False)

            created_files.append(output_file)

        return created_files


def main():
    """Example usage of the WorkflowManager."""
    workflow_manager = WorkflowManager()

    workflows = workflow_manager.list_workflows()
    print("Available workflows:")
    print("\n".join(f"- {workflow}" for workflow in workflows))

    workflow_manager.fetch_workflow("python", [Workflows.TEST])


if __name__ == "__main__":
    main()
