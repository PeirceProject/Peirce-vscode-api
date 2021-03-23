### BEFORE USING

This API is for the Peirce VSCode extension. If you want to use this code, you need the Peirce binary. Place the binary or a softlink to the binary inside api/ called peirce.

For example (in the root directory of this repository):

    ln -s $HOME/Peirce/bin/peirce bin/peirce

### Virtual environment (first time setup)

    python3 -m venv venv
    pip install -r requirements.txt

### How to run

    source venv/bin/activate
    python3 src/api.py
