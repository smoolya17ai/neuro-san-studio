# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
import os
import json
import pathlib
from collections import defaultdict
from typing import Dict


class RepoMetadataExtractor:
    """
    Extracts metadata from a repository, including file types, lines of code,
    key files, languages used, and test directories."""

    CODE_EXTENSIONS = {
        "python": [".py"],
        "ipynb": [".ipynb"],
        "markdown": [".md", ".markdown", ".mdown", ".mkd"],
        "text": [".txt", ".text", ".log"],
        "javascript": [".js", ".jsx", ".mjs", ".cjs"],
        "typescript": [".ts", ".tsx", ".mts", ".cts"],
        "java": [".java"],
        "html": [".html", ".htm"],
        "css": [".css", ".scss"],
        "config": [".json", ".yaml", ".yml", ".toml", ".ini", ".hocon", ".conf"],
        "shell": [".sh", ".bash", ".zsh", ".fish"],
        "sql": [".sql"],
        "xml": [".xml"],
        "yaml": [".yaml", ".yml"],
        "docker": [".dockerfile", "Dockerfile"],
        "c_cpp": [".c", ".cpp", ".h", ".hpp"],
        "go": [".go"],
        "ruby": [".rb"],
        "php": [".php"],
        "rust": [".rs"],
        "kotlin": [".kt", ".kts"],
        "swift": [".swift"],
        "scala": [".scala"]
    }

    KEY_FILES = [
        "README.md", "README.rst", "Dockerfile", "Makefile", "requirements.txt",
        "pyproject.toml", "package.json", "package-lock.json", "yarn.lock",
        ".pre-commit-config.yaml", ".editorconfig", ".env", ".env.example", ".gitignore",
        "docker-compose.yml", "Procfile", "setup.py", "build.gradle", "pom.xml",
        ".github/workflows", ".gitlab-ci.yml", ".flake8", ".pylintrc",
        ".eslintrc", ".stylelintrc", ".prettierrc", "tsconfig.json", "babel.config.js",
        "CMakeLists.txt", "config.json", "config.yaml", "config.yml", "config.toml"
    ]

    ENTRY_POINTS = [
        "main.py", "app.py", "index.js", "server.js", "run.py", "start.py",
        "manage.py", "cli.py", "main.go", "app.rb", "main.rs", "main.kt",
        "main.swift", "main.c", "main.cpp", "main.ts", "main.mjs", "main.cjs"
    ]

    CONFIG_NAMES = [
        "config.py", "pipeline.yaml", "pipeline.yml", "pipeline.json",
        "config.json", "config.yaml", "config.yml", "config.toml",
        "settings.json", "settings.yaml", "settings.yml", "settings.toml",
        "appsettings.json", "appsettings.yaml", "appsettings.yml", "appsettings.toml",
        "config.js", "config.ts", "config.py", "config.rb", "config.go",
        "config.php", "config.ini", "config.hocon", "config.conf"
    ]

    def __init__(self, repo_path: str):
        """
        Initializes the extractor with the path to the repository.
        :param repo_path: Path to the repository directory.
        """
        self.repo_path = repo_path
        self.tree_dict = {"path": [], "depth": [], "type": [], "loc": []}
        self.metadata = {
            "repo_path": repo_path,
            "total_files": 0,
            # "files": [],
            "key_files_present": [],
            "languages": defaultdict(int),
            "total_loc": 0,
            "max_file_loc": 0,
            "max_file": "",
            "test_dirs": [],
            "ci_cd_present": False,
            "entry_points": [],
            "config_files": [],
            "lint_warnings": 0,
            "readme_size": 0,
            "tree": {}
        }

    def get_file_type(self, filename: str) -> str:
        """
        Determines the type of a file based on its extension or name.
        :param filename: Name of the file.
        :return: A string representing the file type (e.g., "python", "javascript", etc.).
        """
        ext = pathlib.Path(filename).suffix.lower()
        for lang, extensions in self.CODE_EXTENSIONS.items():
            if ext in extensions or filename in extensions:
                return lang
        return "other"

    def count_lines(self, file_path: str) -> int:
        """
        Counts the number of lines in a file, ignoring empty lines and comments.
        :param file_path: Path to the file.
        :return: Number of lines of code in the file.
        """
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except Exception:
            return 0
    
    def simplify_paths(self, tree_dict):
        """
        Simplifies the paths in the tree dictionary to a more readable format.
        :param tree_dict: A dictionary containing paths, depths, types, and lines of code.
        :return: A list of simplified paths.
        """
        simplified = []
        seen_dirs = set()
        
        for full_path, depth in zip(tree_dict["path"], tree_dict["depth"]):
            parts = full_path.split(os.sep)
            if depth == 0:
                simplified.append(parts[-1])
            else:
                dir_prefix = os.sep.join(parts[:-1])
                if dir_prefix not in seen_dirs:
                    seen_dirs.add(dir_prefix)
                    simplified.append(dir_prefix + os.sep + parts[-1])
                else:
                    simplified.append("*/" * depth + parts[-1])
        return simplified

    def extract(self) -> Dict:
        """
        Extracts metadata from the repository.
        :return: A dictionary containing the extracted metadata.
        """
        for root, dirs, files in os.walk(self.repo_path):
            for file in files:
                full_path = os.path.join(root, file)
                relative_path = os.path.relpath(full_path, self.repo_path)
                depth = relative_path.count(os.sep)

                file_type = self.get_file_type(file)
                loc = self.count_lines(full_path)

                # self.metadata["files"].append({
                #     "path": relative_path,
                #     "type": file_type,
                #     "loc": loc
                # })

                self.tree_dict["path"].append(relative_path)
                self.tree_dict["depth"].append(depth)
                self.tree_dict["type"].append(file_type)
                self.tree_dict["loc"].append(loc)

                self.metadata["total_files"] += 1
                self.metadata["languages"][file_type] += loc
                self.metadata["total_loc"] += loc

                if loc > self.metadata["max_file_loc"]:
                    self.metadata["max_file_loc"] = loc
                    self.metadata["max_file"] = relative_path

                if file in self.KEY_FILES or relative_path in self.KEY_FILES:
                    self.metadata["key_files_present"].append(file)

                if file in self.ENTRY_POINTS:
                    self.metadata["entry_points"].append(relative_path)

                if file in self.CONFIG_NAMES:
                    self.metadata["config_files"].append(relative_path)

                if "test" in root.lower() and root not in self.metadata["test_dirs"]:
                    self.metadata["test_dirs"].append(root)

                if file.lower() == "readme.md":
                    self.metadata["readme_size"] = loc

                if ".github/workflows" in root or ".gitlab-ci" in root:
                    self.metadata["ci_cd_present"] = True

        self.metadata["languages"] = dict(self.metadata["languages"])
        simplified_paths = self.simplify_paths(self.tree_dict)
        self.tree_dict["path"] = simplified_paths
        self.metadata["tree"] = self.tree_dict
        return self.metadata


if __name__ == "__main__":
    # Replace this path with the path to a real repository
    sample_repo_path = "repos/GenAI-ClaimsAssistant"
    extractor = RepoMetadataExtractor(sample_repo_path)
    repo_metadata = extractor.extract()

    # Save metadata to JSON
    with open("repo_metadata.json", "w") as f:
        json.dump(repo_metadata, f, indent=2)

    # Display nicely formatted metadata
    print(f"Repository Metadata for {sample_repo_path} created successfully at 'repo_metadata.json'.")
