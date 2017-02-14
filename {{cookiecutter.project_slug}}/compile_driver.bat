@echo off
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ok
) else (
    echo This program must be run from an administrator cmd prompt
    goto :fail
)

@echo on

pip install cloudshell-core cloudshell-cli cloudshell-snmp

pyinstaller --onefile driver.spec

taskkill /f /im {{cookiecutter.model_name}}.exe

timeout 3

set driverdir="c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
IF EXIST %driverdir% GOTO :havecs
set driverdir="c:\Program Files (x86)\QualiSystems\TestShell\Server\Drivers"
:havecs


copy dist\{{cookiecutter.model_name}}.exe                     %driverdir%
copy {{cookiecutter.project_slug}}_runtime_configuration.json %driverdir%



copy {{cookiecutter.project_slug}}_datamodel.xml               release\
copy dist\{{cookiecutter.model_name}}.exe                      release\
copy {{cookiecutter.project_slug}}_runtime_configuration.json  release\

:fail
