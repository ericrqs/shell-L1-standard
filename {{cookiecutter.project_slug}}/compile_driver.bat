@echo off
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ok
) else (
    echo This program must be run from an administrator cmd prompt
    goto :fail
)

@echo on

pip install cloudshell-core cloudshell-cli

pyinstaller --onefile driver.spec

taskkill /f /im {{cookiecutter.driver_name.replace(' ', '') }}.exe

timeout 3

set driverdir="c:\Program Files (x86)\QualiSystems\CloudShell\Server\Drivers"
IF EXIST %driverdir% GOTO :havecs
set driverdir="c:\Program Files (x86)\QualiSystems\TestShell\Server\Drivers"
:havecs


copy dist\{{cookiecutter.driver_name.replace(' ', '') }}.exe  %driverdir%
copy {{cookiecutter.project_slug}}_runtime_configuration.json %driverdir%



copy {{cookiecutter.project_slug}}_datamodel.xml               release\
copy dist\{{cookiecutter.driver_name.replace(' ', '') }}.exe        release\
copy {{cookiecutter.project_slug}}_runtime_configuration.json  release\

:fail
