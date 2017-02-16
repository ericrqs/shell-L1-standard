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
from cloudshell.cli.session.tcp_session import TCPSession
from cloudshell.cli.session_pool_manager import SessionPoolManager
from cloudshell.core.logger.qs_logger import get_qs_logger
from cloudshell.networking.cli_handler_impl import CliHandlerImpl

from cloudshell.cli.command_mode import CommandMode


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
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.EXIT_COMMAND)


class {{cookiecutter.model_name.replace(' ', '') }}ConfigCommandMode(CommandMode):
    PROMPT_REGEX = r'[(]config.*[)]#\s*$'
    ENTER_COMMAND = ''
    EXIT_COMMAND = 'exit'

    def __init__(self):
        CommandMode.__init__(self,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.PROMPT_REGEX,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.ENTER_COMMAND,
                             {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.EXIT_COMMAND)


CommandMode.RELATIONS_DICT = {
    {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode: {
        {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode: {
            {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode: {
            }
        }
    }
}

TL1_COMMAND = CommandTemplate('{command}')

SHOW_VERSION = CommandTemplate('show version', action_map=OrderedDict([
    (r'--More--', lambda session, logger: session._send(' ', logger))
]))

SHOW_INTERFACES = CommandTemplate('show interfaces', action_map=OrderedDict([
    (r'--More--', lambda session, logger: session._send(' ', logger))
]))

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


class TL1Session(TCPSession):
    SESSION_TYPE = 'TL1'
    BUFFER_SIZE = 1024

    def __init__(self, host, username, password, port, on_session_start=None, *args, **kwargs):
        super(TL1Session, self).__init__(host, port, on_session_start=on_session_start, *args, **kwargs)
        self._username = username
        self._password = password
        self.switch_name = 'switch-name-not-initialized'
        self._tl1_counter = 0

    def __eq__(self, other):
        """
        :param other:
        :type other: TL1Session
        :return:
        """
        return ConnectionParams.__eq__(self,
                                       other) and self._username == other._username and self._password == other._password

    def connect(self, prompt, logger):
        """
        Open connection to device / create session
        :param prompt:
        :param logger:
        :return:
        """

        if not self._handler:
            self._handler = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = (self.host, self.port)
        self._handler.connect(server_address)
        self._handler.settimeout(self._timeout)

        output = self.hardware_expect('ACT-USER::%s:{counter}::%s;' % (self._username, self._password),
                                      expected_string=None,
                                      logger=logger)
        if '( nil )' in output:
            self.switch_name = ''
            logger.info('Switch name was "( nil )" - using blank switch name')
        else:
            m = re.search(r'(\S+)', output)
            if m:
                self.switch_name = m.groups()[0]
                logger.info('Taking as switch name: "%s"' % self.switch_name)
            else:
                logger.info('Switch name regex not found: %s - using blank switch name' % output)
                self.switch_name = ''
        if self.on_session_start and callable(self.on_session_start):
            self.on_session_start(self, logger)
        self._active = True

    def hardware_expect(self, command, expected_string, logger, action_map=None, error_map=None, timeout=None,
                        retries=None, check_action_loop_detector=True, empty_loop_timeout=None,
                        remove_command_from_output=True, **optional_args):
        self._tl1_counter += 1
        command = command.replace('{counter}', str(self._tl1_counter))
        command = command.replace('{name}', self.switch_name)
        prompt = r'M\s+%d\s+([A-Z ]+)[^;]*;' % self._tl1_counter
        rv = super(TL1Session, self).hardware_expect(command, prompt, logger, action_map, error_map, timeout,
                                                     retries, check_action_loop_detector, empty_loop_timeout,
                                                     remove_command_from_output, **optional_args)
        m = re.search(prompt, rv)
        status = m.groups()[0]
        if status != 'COMPLD':
            raise Exception('Error: Status "%s": %s' % (status, rv))
        return rv


class _{{ cookiecutter.model_name.replace(' ', '') }}CliHandler(CliHandlerImpl):
    def __init__(self, cli, logger, cli_type, host, port, username, password):
        super(_{{ cookiecutter.model_name.replace(' ', '') }}CliHandler, self).__init__(cli, None, logger, None)
        self._cli_type = cli_type
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        modes = CommandModeHelper.create_command_mode()
        self.default_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}DefaultCommandMode]
        self.enable_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}EnableCommandMode]
        self.config_mode = modes[{{ cookiecutter.model_name.replace(' ', '') }}ConfigCommandMode]

        if cli_type.lower() == 'tl1':
            # Sending an empty line to probe for the current prompt doesn't work for TL1.
            # With this workaround, TL1 is always considered to be in the default mode.
            CommandModeHelper.determine_current_mode = staticmethod(lambda o1, o2, o3: self.default_mode)

    @property
    def resource_address(self):
        return self._host

    @property
    def password(self):
        return self._password

    @property
    def cli_type(self):
        return self._cli_type

    @property
    def username(self):
        return self._username

    @property
    def port(self):
        return self._port

    def _new_sessions(self):
        if self.cli_type.lower() == SSHSession.SESSION_TYPE.lower():
            new_sessions = self._ssh_session()
        elif self.cli_type.lower() == TelnetSession.SESSION_TYPE.lower():
            new_sessions = self._telnet_session()
        elif self.cli_type.lower() == TL1Session.SESSION_TYPE.lower():
            new_sessions = self._tl1_session()
        else:
            new_sessions = [self._ssh_session(), self._telnet_session()]
        return new_sessions

    def _ssh_session(self):
        return SSHSession(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                          loop_detector_max_action_loops=10000)

    def _telnet_session(self):
        return TelnetSession(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                             loop_detector_max_action_loops=10000)

    def _tl1_session(self):
        return TL1Session(self.resource_address, self.username, self.password, self.port, self.on_session_start,
                          loop_detector_max_action_loops=10000)


class {{ cookiecutter.model_name.replace(' ', '') }}CliConnection:
    def __init__(self, logger, cli_type, host, port, username, password, session_pool_size=1):
        """
        :param logger: qs_logger
        :param cli_type: str: 'ssh', 'telnet', 'tl1'
        :param host:
        :param port:
        :param username:
        :param password:
        :param session_pool_size:
        """
        self._logger = logger
        session_pool = SessionPoolManager(max_pool_size=session_pool_size, pool_timeout=100)
        self._cli = CLI(session_pool=session_pool)
        self._cli_handler = _{{ cookiecutter.model_name.replace(' ', '') }}CliHandler(self._cli, logger, cli_type, host, port, username, password)

    def get_default_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.default_mode)

    def get_enable_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.enable_mode)

    def get_config_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.config_mode)

    def tl1_command(self, cmd):
        """
        Executes an arbitrary TL1 command, with the switch name and incrementing command number managed automatically.

        :param cmd: A TL1 command like "RTRV-NETYPE:{name}::{counter}:;", where "{name}" and "{counter}" will be automatically substituted with the switch name and an incrementing counter
        :return: str: TL1 command output including the status
        :raises: Exception: If the command status is not COMPLD
        """
        with self.get_default_session() as session:
            return session.send_command(**TL1_COMMAND.get_command(command=cmd))

    def show_version(self):
        with self.get_default_session() as session:
            return session.send_command(**SHOW_VERSION.get_command())

    def show_interfaces(self):
        with self.get_default_session() as session:
            return session.send_command(**SHOW_INTERFACES.get_command())

    def my_command1(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND1.get_command(arg1=input1, arg2=input2))

    def my_command2(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND2.get_command(arg1=input1, arg2=input2))

    def my_command3(self, input1, input2):
        with self.get_config_session() as session:
            return session.send_command(**MY_COMMAND3.get_command(arg1=input1, arg2=input2))

# c = {{ cookiecutter.model_name.replace(' ', '') }}CliConnection(get_qs_logger(), 'tl1', '10.99.99.230', 3082, 'root', 'root', 1)
# print c.tl1_command('RTRV-NETYPE:{name}::{counter}:;')
# print c.tl1_command('RTRV-NETYPE:{name}::{counter}:;')
# print c.tl1_command('RTRV-NETYPE:{name}::{counter}:;')
