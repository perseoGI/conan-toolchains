#!/usr/bin/env python3
import pathlib
import subprocess
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is not installed")

recipes_root = pathlib.Path("recipes")
if not recipes_root.is_dir():
    sys.exit(0)

for recipe_dir in sorted(recipes_root.iterdir()):
    cfg_file = recipe_dir / "config.yml"
    if not cfg_file.is_file():
        continue

    data = yaml.safe_load(cfg_file.read_text()) or {}
    for version in data.get("versions", {}):
        subprocess.run(
            [
                "conan",
                "create",
                str(recipe_dir),
                "--version",
                version,
                "--build",
                "missing",
            ],
            check=True,
        )
