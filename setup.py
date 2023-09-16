"""The python wrapper for Quotex API package setup."""
import shutup
from pathlib import Path
from setuptools import find_packages, setup

shutup.please()

this_dir = Path(__file__).parent

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

with open("README.md", "r", encoding="utf-8") as md:
    readme = md.read()
# -----------------------------------------------------------------------------

setup(
    name="quotexpy",
    version="1.0.3",
    author="Santiago Ramirez",
    author_email="santiirepair@gmail.com",
    description="📈 QuotexPy is a library for interact with qxbroker easily.",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.10",
)
