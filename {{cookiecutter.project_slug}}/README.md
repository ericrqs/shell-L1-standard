# cloudshell-L1-{{cookiecutter.model_name}}

## Installation
Copy to c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers on CloudShell machine:
- {{cookiecutter.model_name}}.exe (If the EXE was downloaded directly from the web, be sure to right click the EXE, open Properties, and *UNBLOCK* the file)
- {{cookiecutter.project_slug}}_runtime_configuration.json

To customize the port, prompt, and other driver-specific settings, edit:
- {{cookiecutter.project_slug}}_runtime_configuration.json

Import {{cookiecutter.project_slug}}_datamodel.xml into Resource Manager

## Usage
- Import {{cookiecutter.project_slug}}_datamodel.xml into Resource Manager
- Create L1 switch resource and set IP address, username, password
- In Configuration view in Resource Manager, push Auto Load
- Create multiple DUTs each with a port subresource
- In Connections view of the L1 switch resource, connect the DUT ports
- Create an empty reservation and add DUTs
- Create a route between two DUTs
- Connect the route
- See log files in c:\Program Files (x86)\QualiSystems\CloudShell\Server\Logs\{{cookiecutter.model_name}}_*\


## Development

### Prerequisites
- Python must be in PATH
- PyInstaller must be installed
  - http://www.pyinstaller.org/
  - Download and extract the zip
  - python setup.py install
- git must be installed
  - https://git-scm.com/
  - Enable Git Bash if asked
- In Git Bash:
  - git clone https://github.com/QualiSystems/cloudshell-L1-{{cookiecutter.model_name}}.git


### Files to edit
- {{cookiecutter.project_slug}}_l1_handler.py
  - Implement the standard L1 driver functions:
    - login
    - logout
    - get_resource_details
    - map_bidi
    - map_uni
    - map_clear
    - map_clear_to
    - get_attribute_value
    - get_state_id
    - set_state_id
  - Load all settings from c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers\{{cookiecutter.project_slug}}_runtime_configuration.json
  - Handle all communication with the device
    - e.g. paramiko
    - e.g. requests
- {{cookiecutter.project_slug}}_datamodel.xml
  - Optionally customize the family or model names for the switch, blade, and port resources 
- {{cookiecutter.project_slug}}_runtime_configuration.json
  - Set default values to be shipped in the default JSON file
  - Define new custom driver settings
  - See notes below

### compile_driver.bat
- Run from a cmd command prompt &mdash; *NOTE: MUST BE RUNNING AS ADMINISTRATOR*
- Kills all {{cookiecutter.model_name}}.exe 
- Copies files to c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers:
  - .\dist\{{cookiecutter.model_name}}.exe
  - .\{{cookiecutter.project_slug}}_runtime_configuration.json
- Copies files to release/ folder:
  - .\dist\{{cookiecutter.model_name}}.exe
  - .\{{cookiecutter.project_slug}}_runtime_configuration.json
  - .\{{cookiecutter.project_slug}}_datamodel.xml

## Notes

Address, username, and password become known to the driver only when 'login' is called. 

The sample code includes hard-coded default values for driver settings.

The port number is not stored on the resource. If you need to customize it, store it in c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers\{{cookiecutter.project_slug}}_runtime_configuration.json.

CLI prompts on some switches can be completely arbitrary. A JSON setting is included for customizing the prompt regex. This is to avoid having to recompile the driver in the event that the customer switch has a bizarre prompt.  

{{cookiecutter.project_slug}}_runtime_configuration.json is not mandatory. If your driver doesn't need any runtime settings, can delete the code that loads the JSON.