import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ReadmeGenerator:
    def __init__(self):
        self.template_dir = Path(__file__).parent / "templates" / "readmes"

    def fetch_readme(
        self,
        project_name: str,
        language: str,
        description: str,
        variables: Optional[Dict] = None,
        output_path: Path = Path("README.md"),
    ):
        """Generate a new README.md file in the repository.

        Args:
            project_name (str): the name of the project
            language (str): the language of the project
            description (str): the description of the project
            variables (Optional[Dict], optional): additional variables to use in the template. Defaults to None.
            output_path (Path, optional): the path to the output directory. Defaults to Path(".github/workflows").
        """
        template_path = self.template_dir / f"{language.lower()}.md"
        if not template_path.exists():
            template_path = self.template_dir / "default.md"

        if not template_path.exists():
            raise ValueError("No README template found")

        vars = {
            "project_name": project_name,
            "language": language.capitalize(),
            "description": description,
            "year": datetime.now().year,
        }

        if variables:
            vars.update(variables)

        with template_path.open() as f:
            template = f.read()

        content = template
        for key, value in vars.items():
            content = re.sub(r"\{\{\s*" + key + r"\s*\}\}", str(value), content)

        output_path.write_text(content)
        return output_path
