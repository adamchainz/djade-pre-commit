# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "packaging",
#     "tomli",
#     "tomli-w",
#     "urllib3",
# ]
# ///
import subprocess
from pathlib import Path

import tomli
import tomli_w
import urllib3
from packaging.requirements import Requirement
from packaging.version import Version


def main():
    with open(Path(__file__).parent / "pyproject.toml", "rb") as f:
        pyproject = tomli.load(f)

    # get current version of black
    deps = pyproject["project"]["dependencies"]
    assert len(deps) == 1
    djade_dep = Requirement(deps[0])
    assert djade_dep.name == "djade"
    djade_specs = list(djade_dep.specifier)
    assert len(djade_specs) == 1
    assert djade_specs[0].operator == "=="
    current_version = Version(djade_specs[0].version)

    # get all versions of djade from PyPI
    resp = urllib3.request("GET", "https://pypi.org/pypi/djade/json")
    if resp.status != 200:
        raise RuntimeError

    versions = [Version(release) for release in resp.json()["releases"]]
    versions = [v for v in versions if v > current_version and not v.is_prerelease]
    versions.sort()

    for version in versions:
        pyproject["project"]["dependencies"] = [f"djade=={version}"]
        with open(Path(__file__).parent / "pyproject.toml", "wb") as f:
            tomli_w.dump(pyproject, f)
        subprocess.run(["git", "add", "pyproject.toml"])
        subprocess.run(["git", "commit", "-m", f"black {version}"])
        subprocess.run(["git", "tag", f"{version}"])


if __name__ == "__main__":
    main()
