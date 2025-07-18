# Copyright (C) 2023-2025 Cognizant Digital Business, Evolutionary AI.
# All Rights Reserved.
# Issued under the Academic Public License.
#
# You can be released from the terms, and requirements of the Academic Public
# License by purchasing a commercial license.
# Purchase of a commercial license is mandatory for any use of the
# neuro-san-studio SDK Software in commercial settings.
#
import fnmatch
import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, Any
from datetime import datetime

from files_to_ignore import IGNORE_DICT


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
        "pyproject.toml", "package-lock.json", "yarn.lock",
        ".pre-commit-config.yaml", ".editorconfig", ".env", ".env.example", ".gitignore",
        "docker-compose.yml", "Procfile", "setup.py", "build.gradle", "pom.xml",
        ".github/workflows", ".gitlab-ci.yml", ".flake8", ".pylintrc",
        ".eslintrc", ".stylelintrc", ".prettierrc", "tsconfig.json", "babel.config.js",
        "CMakeLists.txt", "config.json", "config.yaml", "config.yml", "config.toml"
    ]

    ENTRY_POINTS = [
        "main.py", "app.py", "server.js", "run.py", "start.py",
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

        self.ignore_dict = IGNORE_DICT
        self.repo_path = Path(repo_path)
        self.tree_dict = {"path": [], "depth": []}
        self.metadata = {
            "repo_path": repo_path,
            "total_files": 0,
            "total_loc": 0,
            "languages": defaultdict(int),
            "max_file_loc": 0,
            "max_file": "",
            "test_dirs": 0,
            "ci_cd_present": False,
            "lint_warnings": 0,
            "readme_size": 0,
            "dir_tree_with_file_count": {}
        }

    def get_file_type(self, filename: str) -> str:
        """
        Determines the type of a file based on its extension or name.
        :param filename: Name of the file.
        :return: A string representing the file type (e.g., "python", "javascript", etc.).
        """
        ext = Path(filename).suffix.lower()
        for lang, extensions in self.CODE_EXTENSIONS.items():
            if ext in extensions or filename in extensions:
                return lang
        return "other"

    def count_lines_fast(self, file_path: str) -> int:
        """
        Counts the number of lines in a file, ignoring empty lines and comments.
        :param file_path: Path to the file.
        :return: Number of lines of code in the file.
        """
        lines = 0
        try:
            with open(file_path, "rb") as f:  # read as bytes for speed
                while True:
                    chunk = f.read(1024 * 1024)  # 1MB chunks
                    if not chunk:
                        break
                    lines += chunk.count(b'\n')
        except Exception:
            # Could log errors here
            return 0
        return lines
    
    def is_ignored(self, name: str, ignore_dict) -> bool:
        """
        Checks if a file or directory should be ignored based on the ignore patterns.
        :param name: Name of the file or directory.
        :param ignore_dict: Dictionary of ignore patterns.
        :return: True if the file or directory should be ignored, False otherwise.
        """
        # single check for patterns and dirs
        for pat in ignore_dict:
            if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(name + "/", pat):
                return True
        return False

    def build_tree_with_file_counts(self, root_dir) -> Dict[str, Any]:
        """
        Builds a tree structure of directories with file counts, ignoring specified patterns.
        :param root_dir: The root directory to start building the tree.
        :return: A dictionary representing the directory tree with file counts.
        """
        tree = {}

        # Get and sort entries once
        try:
            entries = sorted(os.listdir(root_dir))
        except PermissionError:
            return {}  # or handle as you wish

        dirs = []
        files_count = 0

        for entry in entries:
            # single pass: ignore check + classify
            # Match against ignore patterns (support wildcards and directory suffix)
            if self.is_ignored(entry, self.ignore_dict):
                continue
            full_path = os.path.join(root_dir, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            elif os.path.isfile(full_path):
                files_count += 1

        # If no valid subdirectories, return just the file count
        if not dirs:
            return files_count

        # Recurse into each valid subdirectory
        for d in dirs:
            tree[d] = self.build_tree_with_file_counts(os.path.join(root_dir, d))

        return tree


    def extract(self) -> Dict:
        """Extracts metadata from the repository.
        :return: A dictionary containing the extracted metadata.
        """
        # Prepare sets for quick lookup
        target_files = set(self.KEY_FILES + self.ENTRY_POINTS)

        # Temporary storage for kec files
        kec_paths, kec_types, kec_locs = [], [], []

        # We will track unique test dirs
        test_dirs_seen = set()

        for path in self.repo_path.rglob("*"):
            # compute relative path once
            rel_path = path.relative_to(self.repo_path)
            parts = rel_path.parts  # tuple of folders/files in hierarchy

            # --- check every part of the path against ignore patterns ---
            skip = False
            for p in parts:
                if self.is_ignored(p, self.ignore_dict):
                    skip = True
                    break
            if skip:
                continue
            # ------------------------------------------------------------

            if path.is_file():
                name = path.name
                loc = self.count_lines_fast(path)
                file_type = self.get_file_type(name)
                rel_path = str(path.relative_to(self.repo_path))

                # aggregate stats
                self.metadata["total_files"] += 1
                self.metadata["languages"][file_type] += loc
                self.metadata["total_loc"] += loc
                if loc > self.metadata["max_file_loc"]:
                    self.metadata["max_file_loc"] = loc
                    self.metadata["max_file"] = rel_path

                # detect special dirs/files
                if "test" in str(path.parent).lower():
                    if str(path.parent) not in test_dirs_seen:
                        test_dirs_seen.add(str(path.parent))
                        self.metadata["test_dirs"] += 1
                if name.lower() == "readme.md":
                    self.metadata["readme_size"] += loc
                if ".github/workflows" in str(path.parent) or ".gitlab-ci" in str(path.parent):
                    self.metadata["ci_cd_present"] = True

                # check KEC files
                if name in target_files:
                    kec_paths.append(rel_path)
                    kec_types.append(file_type)
                    kec_locs.append(loc)

        # finalize language stats
        self.metadata["languages"] = dict(self.metadata["languages"])

        # KEC file info
        self.metadata["kec_files_present"] = {
            "path": kec_paths,
            "type": kec_types,
            "loc": kec_locs
        }

        # Build tree of dirs (after scanning)
        self.metadata["dir_tree_with_file_count"] = self.build_tree_with_file_counts(str(self.repo_path))

        return self.metadata

    def render_tree(self, tree: dict, depth: int = 0) -> str:
        """
        Recursively render the dir_tree_with_file_count into a pretty tree
        using tabs and '-' to indicate depth.
        """
        lines = []
        for name, subtree in tree.items():
            indent = "\t" * depth  # one tab per depth level
            # Add a dash before each entry
            if isinstance(subtree, dict):
                # directory with children
                lines.append(f"{indent}- {name}")
                lines.append(self.render_tree(subtree, depth + 1))
            else:
                # leaf with file count
                lines.append(f"{indent}- {name} ({subtree})")
        return "\n".join(lines)
    
    def render_kec_files(self, kec_dict: dict) -> str:
        """Render the KEC files info dict into a readable text block."""
        paths = kec_dict.get("path", [])
        types = kec_dict.get("type", [])
        locs = kec_dict.get("loc", [])

        lines = []
        for p, t, l in zip(paths, types, locs):
            lines.append(f"  - {p} (type: {t}, loc: {l})")
        return "\n".join(lines)



    def save_metadata(self, metadata: Dict[str, Any], output_dir: str = ".", save_as: str = "json") -> str:
        """
        Saves the extracted metadata to a file in the specified format.
        :param metadata: The metadata dictionary to save.
        :param output_dir: Directory where the metadata file will be saved.
        :param save_as: Format to save the metadata, either "json" or "txt".
        :return: The path to the saved metadata file.
        """
        # validate save_as
        if save_as not in ("json", "txt"):
            raise ValueError("save_as must be either 'json' or 'txt'")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # choose extension and filename
        ext = "json" if save_as == "json" else "txt"
        filename = f"repo_metadata_{timestamp}.{ext}"
        output_path = os.path.join(output_dir, filename)

        if save_as == "json":
            # existing JSON save
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2)
        else:
            # plain text dump (no formatting)
            # -------- Render tree --------
            tree_data = metadata.get("dir_tree_with_file_count", "")
            pretty_tree = self.render_tree(tree_data)
            metadata["dir_tree_with_file_count"] = f"""\n{pretty_tree}\n"""
            
            # -------- Render KEC files --------
            kec_dict = metadata.get("kec_files_present", "")
            pretty_kec = self.render_kec_files(kec_dict)
            metadata["kec_files_present"] = f"""{pretty_kec}"""
            
            # -------- Render languages --------
            lang_data = metadata.get("languages", {})
            pretty_langs = "\n".join([f"  - {k}: {v} LOC" for k, v in lang_data.items()])
            metadata["languages"] = f"""{pretty_langs}\n"""
            # save just that tree text as the file content
            with open(output_path, "w", encoding="utf-8") as f:
                for key, value in metadata.items():
                    # convert everything to string for raw text
                    f.write(f"{key}: {value}\n")

        return output_path



if __name__ == "__main__":
    # Replace this path with the path to a real repository
    sample_repo_path = "repos/GenAI-ClaimsAssistant"
    # sample_repo_path = "repos/nsflow"
    extractor = RepoMetadataExtractor(sample_repo_path)
    repo_metadata = extractor.extract()

    # Save metadata with timestamp
    save_as = "txt"
    output_file = extractor.save_metadata(repo_metadata, output_dir=".", save_as=save_as)

    # Display nicely formatted metadata
    print(f"Repository Metadata for {sample_repo_path} created successfully at 'repo_metadata.'{save_as}.")
