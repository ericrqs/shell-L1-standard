- Install Python 2.7 including pip and add to PATH

- Get PyInstaller
    http://www.pyinstaller.org
    Unzip
    cd pyinstaller-pyinstaller-...
    python setup.py install

- pip install cookiecutter

- In Git Bash:
    git clone https://github.com/ericrqs/shell-L1-standard.git
    cd shell-L1-standard

- Change "Sample" to your driver name in cookiecutter.json

- In Git Bash:
    cookiecutter .
    (push Enter 20 times)

- Customize YourDriverName\<your driver name>_l1_handler.py

- In CMD:
    cd YourDriverName
    compile_driver.bat
