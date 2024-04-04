from setuptools import setup, find_packages

from praxis.__version__ import __version__

with open("README.md", "r", encoding="utf-8") as f:
  long_description = f.read()


extras_fw = [
  "pyusb"
]

extras_http = [
  "requests",
  "types-requests"
]

extras_plate_reading = [
  "pylibftdi",
]

extras_websockets = [
  "websockets"
]

extras_visualizer = extras_websockets

extras_opentrons = [
  "opentrons-http-api-client",
  "opentrons-shared-data"
]

extras_server = [
  "flask[async]",
]


extras_inheco = [
  "hid"
]

extras_agrow = [
  "pymodbus"
]

extras_dev = extras_fw + extras_http + extras_plate_reading + extras_websockets + \
    extras_visualizer + extras_opentrons + extras_server + extras_inheco + extras_agrow + [
    "sphinx_book_theme",
    "myst_nb",
    "sphinx_copybutton",
    "pytest",
    "pytest-timeout",
    "pylint",
    "mypy",
    "responses"
  ]

# Some extras are not available on all platforms. `dev` should be available everywhere
extras_all = extras_dev

setup(
  name="praxis",
  version=__version__,
  packages=find_packages(exclude="tools"),
  description="A hardware agnostic platform for lab automation",
  long_description=long_description,
  long_description_content_type="text/markdown",
  install_requires=["typing_extensions"],
  url="https://github.com/sculptingevolution/pylabpraxis.git",
  author="Sculpting Evolution"
)
