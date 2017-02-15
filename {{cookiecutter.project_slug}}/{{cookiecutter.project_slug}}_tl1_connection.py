# CloudShell L1 driver TL1 connection
#
# It should only be necessary to edit this file if your device has a nonstandard login sequence.
# Otherwise just use it as described below.
#
# Manages TL1 socket connection, login via ACT-USER, switch name, and command counter
#
# Raises an exception if a TL1 command does not return "COMPLD" status
#
# When you get the IP and credentials:
#     tl1 = TL1Connection('123.123.123.234', 22, 'admin', 'password', logger)
#
# Execute an arbitrary TL1 command:
#     result = tl1.command('MY-COMMAND:{name}:my args here:{counter}:;')
#
#   Most commands require a switch name and a counter. Just embed "{name}" and "{counter}"
#   in your command and they will automatically be substituted with the right values.
#

import re
import socket


class {{cookiecutter.model_name.replace(' ', '')}}TL1Connection:
    def __init__(self, logger, address, port, username, password, connect_immediately=True):
        """
        Connects to the device
        :param logger: qs_logger
        :param address:
        :param port:
        :param username:
        :param password:
        :param connect_immediately: bool: True to open the connection before leaving the constructor
        """
        self._address = address
        self._port = port
        self._username = username
        self._password = password
        self._logger = logger
        self._sock = None
        self._counter = 0
        self._switch_name = 'bad-switch-name'
        if connect_immediately:
            self.connect()

    def __del__(self):
        self.disconnect()

    def connect(self):
        """
        Connect to the device, log in, and try to determine the switch name
        :return: None
        """
        self._logger.info('Connecting to %s...' % self._address)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self._address, self._port))
        self._counter = 0

        self.command('ACT-USER::%s:{counter}::%s;' % (self._username, self._password))

        s = self.command('RTRV-HDR:::{counter}:;')
        if '( nil )' in s:
            self._switch_name = ''
            self._logger.info('Switch name was "( nil )" - using blank switch name')
        else:
            m = re.search(r'(\S+)', s)
            if m:
                self._switch_name = m.groups()[0]
                self._logger.info('Taking as switch name: "%s"' % self._switch_name)
            else:
                self._logger.info('Switch name regex not found: %s - using blank switch name' % s)
                self._switch_name = ''
        self._logger.info('Connected')

    def _write(self, s):
        while s:
            try:
                n = self._sock.send(s)
            except Exception as e:
                self._logger.info('Caught send failure %s; reconnecting and retrying' % str(e))
                self.reconnect()
                n = self._sock.send(s)
            self._logger.info('sent <<<%s>>>' % s[0:n])
            s = s[n:]

    def _read_until(self, regex):
        buf = ''
        while True:
            b = self._sock.recv(1024)
            self._logger.info('recv returned <<<%s>>>' % b)
            if b:
                buf += b
            if re.search(regex, buf):
                self._logger.info('read complete: <<<%s>>>' % buf)
                return buf
            if not b:
                raise Exception('End of recv stream without encountering termination pattern "%s"' % regex)

    def command(self, cmd):
        """
        Send a command and return the result. Automatically substitute the switch name and command counter
        :param cmd: str: The TL1 command to execute, e.g. "RTRV-NETYPE:{name}::{counter}:;" where "{name}" and "{counter}" -- both optional -- will be substituted automatically with the switch name and command serial number
        :return: str: full command output
        """
        cmd = cmd.replace('{name}', self._switch_name)
        self._counter += 1
        cmd = cmd.replace('{counter}', str(self._counter))
        prompt = r'M\s+%d\s+([a-zA-Z ]+)[^;]*;' % self._counter

        self._write(cmd + '\n')
        rv = self._read_until(prompt)
        m = re.search(prompt, rv)
        status = m.groups()[0]
        if status != 'COMPLD':
            raise Exception('Error: Status "%s": %s' % (status, rv))
        return rv

    def disconnect(self):
        """
        Close the connection socket
        :return: None
        """
        self._logger.info('Disconnecting...')
        try:
            self._sock.close()
        except:
            pass
        self._sock = None
        self._logger.info('Disconnected')

    def reconnect(self):
        """
        Disconnect and reconnect
        :return: None
        """
        self.disconnect()
        self.connect()
