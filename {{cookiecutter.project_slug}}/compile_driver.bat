pyinstaller --onefile driver.spec

taskkill /f /im {{cookiecutter.model_name}}.exe

sleep 3

set driverdir="c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
IF EXIST %driverdir% GOTO :havecs
set driverdir="c:\Program Files (x86)\QualiSystems\TestShell\Server\Drivers"
:havecs

copy dist\{{cookiecutter.model_name}}.exe                     %driverdir%
copy {{cookiecutter.project_slug}}_runtime_configuration.json %driverdir%



copy {{cookiecutter.project_slug}}_datamodel.xml               release\
copy dist\{{cookiecutter.model_name}}.exe                      release\
copy {{cookiecutter.project_slug}}_runtime_configuration.json  release\

