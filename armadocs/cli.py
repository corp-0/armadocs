#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Entry point for the script
"""

import click
from version import __version__, __release__
from classes import YAMLGenerator, DocGenerator


@click.group()
def main():
    """This script generates documentation for your Arma3 project. \
To get started navigate to your project root directory and run the script \
with the command 'init'"""
    pass


@main.command()
def version():
    """Shows current version"""
    click.echo(f"current version: {__version__}")


@main.command()
def init():
    """Starts the YAML generator at current work directory"""
    YAMLGenerator()


@main.command()
def generate():
    """Reads the YAML data and generates the documentation"""
    DocGenerator()

if __name__ == "__main__":
    main()
