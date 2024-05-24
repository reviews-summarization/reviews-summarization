#!/usr/bin/env python3

from pathlib import Path

from setuptools import setup

REPO_ROOT = Path(__file__).parent.resolve()

setup(
  name='reviews-summarization',
  version='0.0.0',
  long_description=(REPO_ROOT / 'README.md').read_text(),
  long_description_content_type='text/markdown',
  packages = [],
  install_requires=[
    'requests',
    'beautifulsoup4'
  ],
  python_requires='>=3.8',
  extras_require={
    'dev': [
      # linting
      "pylint",
      "pre-commit",

      # testing
      "pytest",

      #server
      "flask",
      "mysql-connector-python",
      "waitress",

      #bot
      "python-telegram-bot",
    ],
  }
)
