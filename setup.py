"""The python wrapper for IQ Option API package setup."""
from pathlib import Path

from setuptools import find_packages, setup

this_dir = Path(__file__).parent
module_dir = this_dir / "vault_decryptor"

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

# -----------------------------------------------------------------------------

setup(
    name="quotex-api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
)
