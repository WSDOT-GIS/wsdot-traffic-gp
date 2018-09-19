"""Creates the Python package files
"""

from __future__ import print_function, unicode_literals
from subprocess import run
# from os import remove

# Generate ReStructured Text from README markdown
# print("Converting README from Markdown to ReStructured Text...")
# run(["pandoc", "-o", "README.rst", "-f", "rst", "-t", "markdown", "README.md"], check=True)

print("Creating Package files...")
print("\tCreating source distribution...")
run(["python", "setup.py", "sdist"], check=True)

print("\tCreating Universal Wheel...")
run(["python", "setup.py", "bdist_wheel"], check=True)

# remove("README.rst")
