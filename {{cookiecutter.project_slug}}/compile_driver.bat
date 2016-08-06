pyinstaller --onefile driver.spec

taskkill /f /im {{cookiecutter.model_name}}.exe

sleep 3

copy dist\{{cookiecutter.model_name}}.exe                     "c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
copy {{cookiecutter.project_slug}}_runtime_configuration.json "c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"

copy {{cookiecutter.project_slug}}_datamodel.xml               release\
copy dist\{{cookiecutter.model_name}}.exe                      release\
copy {{cookiecutter.project_slug}}_runtime_configuration.json  release\

