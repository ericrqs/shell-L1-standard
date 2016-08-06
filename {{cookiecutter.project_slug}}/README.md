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
- See log files in c:\Program Files (x86)\QualiSystems\CloudShell\Server\Logs\\{{cookiecutter.model_name}}_*\


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


### What to edit
- {{cookiecutter.project_slug}}_l1_handler.py
  - Fill in the implementation for any relevant L1 driver functions: login, logout, get_resource_details, map_bidi, map_uni, map_clear, map_clear_to, get_attribute_value, get_state_id, set_state_id
  - Load all settings from c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers\\{{cookiecutter.project_slug}}_runtime_configuration.json
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
  - .\dist\\{{cookiecutter.model_name}}.exe
  - .\\{{cookiecutter.project_slug}}_runtime_configuration.json
- Copies files to release/ folder:
  - .\dist\\{{cookiecutter.model_name}}.exe
  - .\\{{cookiecutter.project_slug}}_runtime_configuration.json
  - .\\{{cookiecutter.project_slug}}_datamodel.xml

## Notes

The only .py you should need to edit is {{cookiecutter.project_slug}}_l1_handler.py.

The address, username, and password of the switch resource become known to the driver only when 'login' is called. 

The port number is not stored on the resource. If it can't just be hard coded in the driver, take the setting from c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers\\{{cookiecutter.project_slug}}_runtime_configuration.json.

### JSON config
The sample code includes hard-coding of default values for the JSON settings.

CLI prompts on some switches can be completely arbitrary. A JSON setting is included for customizing the prompt regex. This is to avoid having to recompile the driver in the event that the customer switch has been given a bizarre prompt. If you don't have such prompt issues, you can delete all code related to this setting.

{{cookiecutter.project_slug}}_runtime_configuration.json is not mandatory. If your driver doesn't need any runtime settings, you can delete all the code in {{cookiecutter.project_slug}}_l1_handler.py that deals with the JSON.

### Driver implementation tips

Even if your driver makes REST calls and doesn't maintain a persistent connection, you still need 'login' just to save the address, username, and password for use by in the mapping functions.   

#### SSH

For an SSH device, it is convenient to use Paramiko.

    import paramiko
    # ...
        def receive(self):
            # read until the prompt regex is found
            prompt_regex = '>'
            rv = ''
            while True:
                self.channel.settimeout(30)
                r = self.channel.recv(2048)
                if r:
                    rv += r
                t = re.sub(r'\x1b\[\d+m, '', rv)
                if not r or len(re.findall(prompt_regex, t)) > 0:
                    return t

        def do_command(self, command):
            self.channel.send(command + '\n')
            return self.receive()
            
        def login(self, address, username, password)
            ssh = paramiko.SSHClient()
            ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(address,
                        port=22,
                        username=username,
                        password=password,
                        look_for_keys=True)
            self.channel = ssh.invoke_shell()
            self.receive() # eat banner
         

Communication with your device may have unique timing requirements. 

You might have to handle SSH connections closed by the remote host. It never hurts to disconnect and reconnect.

To log in with an RSA key file (id_rsa), pass look_for_keys=True to the SSH connect() as shown above. Paramiko will search for ~/.ssh/id_rsa. The driver runs in the system account, so the key file should be at C:\Windows\System32\Config\systemprofile\\.ssh\id_rsa. Continue to specify the username and password on the resource. The password will be used to decrypt the id_rsa file, and along with the username this key will be used to log in. This feature has never been tested with a blank password, so create the id_rsa with a password to be safe.    

If you connect to a color terminal, the returned data may be polluted with control sequences in the form ESC[123m (regex: r'\x1b\\[\d+m'). This could interfere with your detection of the prompt regex. Buffer all the received data and look for the prompt regex in a separate copy of the data with the control sequences deleted.


