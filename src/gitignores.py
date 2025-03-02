from pathlib import Path
from typing import List
import requests

class GitignoreManager:
    """Manages fetching and creation of .gitignore files from GitHub's templates."""
    
    def __init__(self):
        self.github_api = "https://api.github.com/repos/github/gitignore/contents"
        self.headers = {"Accept": "application/json"}

    def list_available_templates(self) -> List[str]:
        """Get a list of all available .gitignore templates."""
        response = self._make_request(self.github_api)
        
        templates = []
        for item in response.json():
            if item["name"].endswith(".gitignore"):
                # Remove .gitignore extension for cleaner names
                template_name = item["name"].replace(".gitignore", "")
                templates.append(template_name)
                
        return sorted(templates)

    def create_gitignore(self, language: str, output_path: Path = Path(".gitignore")):
        """Create a .gitignore file for the specified language/framework."""
        content = self._get_template_content(language)
        output_path.write_text(content)
        print(f"Created .gitignore for {language} at {output_path}")

    def _get_template_content(self, language: str) -> str:
        """Fetch the content of a specific gitignore template."""
        template_url = f"{self.github_api}/{language}.gitignore"
        response = self._make_request(template_url)
        
        download_url = response.json()["download_url"]
        template_response = self._make_request(download_url)
        
        return template_response.text

    def _make_request(self, url: str) -> requests.Response:
        """Make an HTTP request and handle potential errors."""
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(
                f"GitHub API request failed: {response.status_code}\n"
                f"URL: {url}"
            )
            
        return response

def main():
    """Example usage of the GitignoreManager."""
    gitignore = GitignoreManager()
    
    # Show available templates
    templates = gitignore.list_available_templates()
    print("Available templates:")
    print("\n".join(f"- {template}" for template in templates))
    
    # Create a Python .gitignore
    gitignore.create_gitignore("Python")

if __name__ == "__main__":
    main()