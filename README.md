- Install Python 2.7
    - Including pip
    - Add to PATH

- Get PyInstaller
    - http://www.pyinstaller.org
    - Unzip
    - cd pyinstaller-pyinstaller-...
    - python setup.py install

- pip install cookiecutter

- In Git Bash:
    - git clone https://github.com/ericrqs/shell-L1-standard.git
    - cd shell-L1-standard
    - cookiecutter .
    - Replace "Sample" with your resource model name (spaces ok)
    - Push Enter many times to accept other defaults

- If you entered "Your Model Name", a folder "your_model_name" will be created containing the generated files

- Customize the code according to your_model_name\\README.md:
    - your_model_name_l1_handler.py
    - your_model_name_runtime_configuration.json
    - your_model_name_tl1_connection.py or your_model_name_cli_connection.py if using TL1 or Telnet/SSH

- In CMD:
    - compile_driver.bat

- Add the contents of your_model_name at the root of a new GitHub project
