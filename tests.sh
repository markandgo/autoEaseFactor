#!/usr/bin/env bash
bash anki_testing/install_anki.sh
# newer versions read __init__.py on the root level which errors
#  as of jan 2019, is this fixed?
# python3 -m pip install pytest==3.7.1
python3 -m pytest tests
