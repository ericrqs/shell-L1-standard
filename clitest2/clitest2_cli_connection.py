# CloudShell L1 driver Telnet or SSH connection
#
# Uses the standard CloudShell CLI package.
#
# Edit this file to define command modes (enable mode, config mode) and custom CLI commands
# (including interactive y/n responses) for your device.
#

from collections import OrderedDict

from cloudshell.cli.command_mode_helper import CommandModeHelper
from cloudshell.cli.command_template.command_template import CommandTemplate
from cloudshell.networking.cli_handler_impl import CliHandlerImpl
from cloudshell.networking.devices.driver_helper import get_cli

from cloudshell.cli.command_mode import CommandMode


class Clitest2DefaultCommandMode(CommandMode):
    def __init__(self):
        CommandMode.__init__(self, r'>\s*$', '', 'exit')


class Clitest2EnableCommandMode(CommandMode):
    def __init__(self):
        CommandMode.__init__(self, r'#\s*$', 'enable', 'exit')


class Clitest2ConfigCommandMode(CommandMode):
    def __init__(self):
        CommandMode.__init__(self, r'\(config.*\)#\s*$', 'configure terminal', 'exit')


CommandMode.RELATIONS_DICT = {
    Clitest2DefaultCommandMode: {
        Clitest2EnableCommandMode: {
            Clitest2ConfigCommandMode: {
            }
        }
    }
}

SHOW_VERSION = CommandTemplate('show version')
SHOW_INTERFACES = CommandTemplate('show interfaces')
MY_COMMAND1 = CommandTemplate('my_command1 {arg1} {arg2}', action_map=OrderedDict({
                           r'\[confirm\]': lambda session, logger: session.send_line('', logger),
                           r'\[Y/N\]': lambda session, logger: session.send_line('y', logger),
                           '\(Y/N\)': lambda session, logger: session.send_line('y', logger)}))
MY_COMMAND2 = CommandTemplate('my_command2 {arg1} {arg2}', action_map=OrderedDict({
                           r'\[confirm\]': lambda session, logger: session.send_line('', logger),
                           r'\[Y/N\]': lambda session, logger: session.send_line('y', logger),
                           '\(Y/N\)': lambda session, logger: session.send_line('y', logger)}))
MY_COMMAND3 = CommandTemplate('my_command3 {arg1} {arg2}', action_map=OrderedDict({
                           r'\[confirm\]': lambda session, logger: session.send_line('', logger),
                           r'\[Y/N\]': lambda session, logger: session.send_line('y', logger),
                           '\(Y/N\)': lambda session, logger: session.send_line('y', logger)}))


class Clitest2CliHandler(CliHandlerImpl):

    def __init__(self, cli, logger, cli_type, host, port, username, password):
        super(Clitest2CliHandler, self).__init__(cli, None, logger, None)
        self._cli_type = cli_type
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        modes = CommandModeHelper.create_command_mode()
        self.default_mode = modes[Clitest2DefaultCommandMode]
        self.enable_mode = modes[Clitest2EnableCommandMode]
        self.config_mode = modes[Clitest2ConfigCommandMode]

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

    def on_session_start(self, session, logger):
        super(Clitest2CliHandler, self).on_session_start(session, logger)


class Clitest2CliConnection:
    def __init__(self, logger, cli_type, host, port, username, password, session_pool_size=1):
        """
        :param logger: qs_logger
        :param cli_type: str: 'ssh' or 'telnet'
        :param host:
        :param port:
        :param username:
        :param password:
        :param session_pool_size:
        """
        self._logger = logger
        self._cli = get_cli(session_pool_size)
        self._cli_handler = Clitest2CliHandler(self._cli, logger, cli_type, host, port, username, password)

    def get_default_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.default_mode)

    def get_enable_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.enable_mode)

    def get_config_session(self):
        return self._cli_handler.get_cli_service(self._cli_handler.config_mode)

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

