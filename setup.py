"""Setup script for Praxis, a hardware agnostic platform for managing lab automation."""

from setuptools import find_packages, setup  # type: ignore

from .__version__ import __version__

with open("README.md", "r", encoding="utf-8") as f:
  long_description = f.read()


extras_fw = ["pyusb"]

extras_http = ["requests", "types-requests"]

extras_plate_reading = [
  "pylibftdi",
]

extras_websockets = ["websockets"]

extras_visualizer = extras_websockets

extras_opentrons = ["opentrons-http-api-client", "opentrons-shared-data"]

extras_server = [
  "flask[async]",
]


extras_inheco = ["hid"]

extras_agrow = ["pymodbus"]

extras_email = ["boto3"]

extras_dev = (
  extras_fw
  + extras_http
  + extras_plate_reading
  + extras_websockets
  + extras_visualizer
  + extras_opentrons
  + extras_server
  + extras_inheco
  + extras_agrow
  + [
    "sphinx_book_theme",
    "myst_nb",
    "sphinx_copybutton",
    "pytest",
    "pytest-timeout",
    "pylint",
    "mypy",
    "responses",
    "freezegun",
    "fakeredis",
  ]
)

# Some extras are not available on all platforms. `dev` should be available everywhere
extras_all = extras_dev

setup(
  name="praxis",
  version=__version__,
  packages=find_packages(exclude="tools"),
  description="A hardware agnostic platform for lab automation",
  long_description=long_description,
  long_description_content_type="text/markdown",
  install_requires=[
    "typing_extensions",
    "pylabrobot git+https://github.com/pylabrobot/pylabrobot.git@main",
    "pydantic>=2.0.0",
    "sqlalchemy[asyncio]",
    "asyncpg>0.27.0",
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.34.0uuid-utils>=0.11.0",
  ],
  url="https://github.com/maraxen/pylabpraxis.git",
  author="Marielle Russo",
)
