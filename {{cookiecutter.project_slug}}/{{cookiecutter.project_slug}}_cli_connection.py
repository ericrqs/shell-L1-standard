# CloudShell L1 driver SSH, Telnet, or TL1 connection
#
# Uses the standard CloudShell CLI package.
#
# Edit this file to define command modes (enable mode, config mode) and custom CLI commands
# (including interactive y/n responses) for your device.
#
# For TL1, prompts and modes are ignored.
#
# Note that prompt regexes can also be overridden from the runtime configuration JSON.
#

import re
import socket
from collections import OrderedDict

from cloudshell.cli.cli import CLI
from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.cli.session.connection_params import ConnectionParams
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.session.scpi_session import SCPISession
from cloudshell.cli.session.tl1_session import TL1Session
from cloudshell.cli.session.tcp_session import TCPSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.networking.cli_handler_impl import CliHandlerImpl

from cloudshell.cli.command_mode import CommandMode


class {{ cookiecutter.model_name.replace(' ', '') }}RawCommandMode(CommandMode):
    PROMPT_REGEX = r'DUMMY_PROMPT'
    ENTER_COMMAND = ''
    EXIT_COMMAND = ''

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}RawCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}RawCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}RawCommandMode.EXIT_COMMAND)


class {{ cookiecutter.model_name.replace(' ', '') }}DefaultCommandMode(CommandMode):
    PROMPT_REGEX = r'>\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode.EXIT_COMMAND)


class {{cookiecutter.model_name.replace(' ', '') }}EnableCommandMode(CommandMode):
    PROMPT_REGEX = r'#\s*$'
    ENTER_COMMAND = 'enable'
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.EXIT_COMMAND)


class {{cookiecutter.model_name.replace(' ', '') }}ConfigCommandMode(CommandMode):
    PROMPT_REGEX = r'[(]config.*[)]#\s*$'
    ENTER_COMMAND = 'configure terminal'
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    {{cookiecutter.model_name.replace(' ', '')}}RawCommandMode: {
        {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode: {
            {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode: {
                {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode: {
                }
            }
        }
    }
}

TL1_COMMAND = CommandTemplate('{command}')
SCPI_COMMAND = CommandTemplate('{command}')

SHOW_VERSION = CommandTemplate('show version', action_map=OrderedDict([
    (r'--More--', lambda session, logger: session._send(' ', logger))
]))

SHOW_INTERFACES = CommandTemplate('show interfaces', action_map=OrderedDict([
    (r'--More--', lambda session, logger: session._send(' ', logger))
]))

INTERFACE_ETHERNET = CommandTemplate('interface Ethernet{port}')
SWITCHPORT_ACCESS_VLAN = CommandTemplate('switchport access vlan {vlan}')
NO_SWITCHPORT_ACCESS_VLAN = CommandTemplate('no switchport access vlan {vlan}')
EXIT = CommandTemplate('exit')

MY_COMMAND1 = CommandTemplate('my_command1 {arg1} {arg2}', action_map=OrderedDict([
    (r'\[confirm\]', lambda session, logger: session.send_line('', logger)),
    (r'\[Y/N\]', lambda session, logger: session.send_line('y', logger)),
    (r'\(Y/N\)', lambda session, logger: session.send_line('y', logger)),
]))

MY_COMMAND2 = CommandTemplate('my_command2 {arg1} {arg2}', action_map=OrderedDict([
    (r'\[confirm\]', lambda session, logger: session.send_line('', logger)),
    (r'\[Y/N\]', lambda session, logger: session.send_line('y', logger)),
    (r'\(Y/N\)', lambda session, logger: session.send_line('y', logger)),
]))

MY_COMMAND3 = CommandTemplate('my_command3 {arg1} {arg2}', action_map=OrderedDict([
    (r'\[confirm\]', lambda session, logger: session.send_line('', logger)),
    (r'\[Y/N\]', lambda session, logger: session.send_line('y', logger)),
    (r'\(Y/N\)', lambda session, logger: session.send_line('y', logger)),
]))


class {{ cookiecutter.model_name.replace(' ', '') }}CliConnection:
    def __init__(self, logger, session_pool_size=1):
        """
        :param logger: qs_logger
        :param cli_type: str: 'ssh', 'telnet', 'tl1'
        :param session_pool_size:
        """
        self._logger = logger
        self._logger.info('Create {{ cookiecutter.model_name.replace(' ', '') }}CliConnection')
        session_pool = SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=100)
        self._cli = CLI(session_pool=session_pool)
        self._cli_handler = _{{ cookiecutter.model_name.replace(' ', '') }}CliHandler(self._cli, logger)

    def __init__(self, logger, session_pool_size=1):
        """
        :param logger: qs_logger
        :param cli_type: str: 'ssh', 'telnet', 'tl1'
        :param session_pool_size:
        """
        self._logger = logger
        self._logger.info('Create PolatisCliConnection')

        self.on_session_start = None
        self.resource_address = None
        self.port = None
        self.username = None
        self.password = None
        self.cli_type = None

        session_pool = SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=100)
        self._cli = CLI(session_pool=session_pool)
        modes = CommandModeHelper.create_command_mode()
        self.raw_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}RawCommandMode]
        self.default_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}DefaultCommandMode]
        self.enable_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}EnableCommandMode]
        self.config_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}ConfigCommandMode]

    def set_resource_address(self, addr):
        self.resource_address = addr

    def set_port(self, port):
        self.port = port

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password

    def set_cli_type(self, cli_type):
        self.cli_type = cli_type

    def _make_session(self):
        if self.cli_type.lower() == 'ssh':
            return SSHSession(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                              loop_detector_max_action_loops=10000)
        elif self.cli_type.lower() == 'telnet':
            return TelnetSession(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                                 loop_detector_max_action_loops=10000)
        elif self.cli_type.lower() == 'tl1':
            return TL1Session(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                              loop_detector_max_action_loops=10000)
        elif self.cli_type.lower() == 'scpi':
            return SCPISession(self.resource_address, self.port, self.on_session_start,
                               loop_detector_max_action_loops=10000)
        else:
            raise Exception('Unsupported CLI type "%s"' % self.cli_type)

    def get_raw_session(self):
        return self._cli.get_session(self._make_session(), self.raw_mode, self._logger)

    def get_default_session(self):
        return self._cli.get_session(self._make_session(), self.default_mode, self._logger)

    def get_enable_session(self):
        return self._cli.get_session(self._make_session(), self.enable_mode, self._logger)

    def get_config_session(self):
        return self._cli.get_session(self._make_session(), self.config_mode, self._logger)

    def scpi_command(self, cmd, ):
        """
        Executes an arbitrary SCPI command

        :param cmd: An SCPI command like ":OXC:SWITch:CONNect:STATe?"
        :return: str: SCPI command output including the status
        :raises: Exception: If the command status is < 0
        """
        with self.get_raw_session() as session:
            return session.send_command(**SCPI_COMMAND.get_command(command=cmd))

    def tl1_command(self, cmd):
        """
        Executes an arbitrary TL1 command, with the switch name and incrementing command number managed automatically.

        :param cmd: A TL1 command like "RTRV-NETYPE:{name}::{counter}:;", where "{name}" and "{counter}" will be automatically substituted with the switch name and an incrementing counter
        :return: str: TL1 command output including the status
        :raises: Exception: If the command status is not COMPLD
        """
        with self.get_raw_session() as session:
            return session.send_command(**TL1_COMMAND.get_command(command=cmd))

    def show_version(self):
        with self.get_default_session() as session:
            return session.send_command(**SHOW_VERSION.get_command())

    def show_interfaces(self):
        with self.get_default_session() as session:
            return session.send_command(**SHOW_INTERFACES.get_command())

    def set_vlan(self, port, vlan):
        with self.get_config_session() as session:
            session.send_command(**INTERFACE_ETHERNET.get_command(port=port))
            session.send_command(**SWITCHPORT_ACCESS_VLAN.get_command(vlan=vlan))
            session.send_command(**EXIT.get_command())

    def unset_vlan(self, port, vlan):
        with self.get_config_session() as session:
            session.send_command(**INTERFACE_ETHERNET.get_command(port=port))
            session.send_command(**NO_SWITCHPORT_ACCESS_VLAN.get_command(vlan=vlan))
            session.send_command(**EXIT.get_command())

    def my_command1(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND1.get_command(arg1=input1, arg2=input2))

    def my_command2(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND2.get_command(arg1=input1, arg2=input2))

    def my_command3(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND3.get_command(arg1=input1, arg2=input2))
