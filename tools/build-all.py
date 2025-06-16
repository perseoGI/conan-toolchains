import pathlib
import subprocess
import yaml


def load_versions(recipe_dir: pathlib.Path) -> dict[str, dict]:
    """
    Return the mapping {version -> info} defined in `config.yml`.
    If the file does not exist, return an empty dict.
    """
    cfg = recipe_dir / "config.yml"
    if not cfg.is_file():
        return {}
    data = yaml.safe_load(cfg.read_text()) or {}
    return data.get("versions", {})


for recipe_dir in sorted(pathlib.Path("recipes").iterdir()):
    versions = load_versions(recipe_dir)
    for version, info in versions.items():
        folder = info.get("folder", ".")
        recipe_path = recipe_dir / folder
        conanfile = recipe_path / "conanfile.py"
        print(f"::group::{recipe_dir.name}/{version}")
        try:
            subprocess.run(
                [
                    "conan",
                    "create",
                    str(recipe_path),
                    "--version",
                    version,
                    "--build",
                    "missing",
                    "--build-require",
                ],
                check=True,
            )
        finally:
            print("::endgroup::")
