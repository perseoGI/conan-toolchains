#!/usr/bin/env python3
import json
import pathlib
import subprocess
import yaml

RECIPES = pathlib.Path("recipes")


def load_versions(recipe_dir: pathlib.Path) -> dict:
    cfg = recipe_dir / "config.yml"
    if not cfg.is_file():
        return {}
    return yaml.safe_load(cfg.read_text() or "").get("versions", {})


for recipe_dir in sorted(RECIPES.iterdir()):
    versions = load_versions(recipe_dir)

    for version, info in versions.items():
        recipe_path = recipe_dir / info.get("folder", ".")

        inspect_json = subprocess.check_output(
            ["conan", "inspect", str(recipe_path / "conanfile.py"), "--format=json"],
            text=True,
        )
        recipe_name = json.loads(inspect_json)["name"]

        cmd = [
            "conan",
            "create",
            str(recipe_path),
            "--version",
            version,
            "--build",
            "missing",
            "--build-test",
            f"{recipe_name}/*",
            "--build-require",
            "-pr:h",
            str(recipe_path / "test_package" / "profile"),
            "-c",
            "tools.build.cross_building:can_run=True",
        ]

        print(f"::group::{recipe_name}/{version}", flush=True)

        try:
            print("executing:", " ".join(cmd), flush=True)
            subprocess.run(cmd, check=True)
        finally:
            print("::endgroup::", flush=True)
