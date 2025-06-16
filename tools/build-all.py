import pathlib
import subprocess
import yaml

RECIPES = pathlib.Path("recipes")
PROFILES = pathlib.Path("profiles")


def load_versions(recipe_dir: pathlib.Path) -> dict:
    cfg = recipe_dir / "config.yml"
    if not cfg.is_file():
        return {}
    return yaml.safe_load(cfg.read_text() or "").get("versions", {})


for recipe_dir in sorted(RECIPES.iterdir()):
    versions = load_versions(recipe_dir)
    profile = PROFILES / recipe_dir.name

    for version, info in versions.items():
        recipe_path = recipe_dir / info.get("folder", ".")
        cmd = [
            "conan",
            "create",
            str(recipe_path),
            "--version",
            version,
            "--build",
            "missing",
            "--build-test",
            f"{recipe_dir}/*",
            "--build-require",
            "-pr:h",
            f"{profile}-base",
        ]
        print(f"::group::{recipe_dir.name}/{version}")
        try:
            print(f"executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        finally:
            print("::endgroup::")
