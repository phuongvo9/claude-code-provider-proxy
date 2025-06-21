#!/usr/bin/env zsh

source .venv/bin/activate
pip install -e .
.venv/bin/python .venv/bin/pytest