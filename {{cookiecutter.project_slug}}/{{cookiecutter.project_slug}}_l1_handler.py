import json
import os

import sys

from l1_driver_resource_info import L1DriverResourceInfo
from l1_handler_base import L1HandlerBase
from {{cookiecutter.project_slug}}_cli_connection import {{cookiecutter.model_name.replace(' ', '')}}CliConnection, {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode, {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode, {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode


class {{cookiecutter.model_name.replace(' ', '')}}L1Handler(L1HandlerBase):
    
    def __init__(self, logger):
        self._logger = logger

        self._host = None
        self._username = None
        self._password = None
        self._port = None

        self._switch_family = None
        self._blade_family = None
        self._port_family = None
        self._switch_model = None
        self._blade_model = None
        self._port_model = None
        self._blade_name_template = None
        self._port_name_template = None

        self._connection = None

    def login(self, address, username, password):
        """
        :param address: str
        :param username: str
        :param password: str
        :return: None
        """
        self._host = address
        self._username = username
        self._password = password

        try:
            with open(os.path.join(os.path.dirname(sys.argv[0]), '{{cookiecutter.project_slug}}_runtime_configuration.json')) as f:
                o = json.loads(f.read())
        except Exception as e:
            self._logger.warn('Failed to read JSON config file: ' + str(e))
            o = {}

        self._port = o.get("common_variable", {}).get("connection_port", 22)
        {{cookiecutter.model_name.replace(' ', '')}}DefaultCommandMode.PROMPT_REGEX = o.get("common_variable", {}).get("default_prompt", r'>\s*$')
        {{cookiecutter.model_name.replace(' ', '')}}EnableCommandMode.PROMPT_REGEX = o.get("common_variable", {}).get("enable_prompt", r'#\s*$')
        {{cookiecutter.model_name.replace(' ', '')}}ConfigCommandMode.PROMPT_REGEX = o.get("common_variable", {}).get("config_prompt", r'[(]config.*[)]#\s*$')

        self._switch_family, self._blade_family, self._port_family = o.get("driver_variable", {}).get("resource_family_name",
            ['{{cookiecutter.family_name}}', '{{cookiecutter.family_name}} Blade', '{{cookiecutter.family_name}} Port'])
        self._switch_model, self._blade_model, self._port_model = o.get("driver_variable", {}).get("resource_model_name",
            ['{{cookiecutter.model_name}}', 'Blade {{cookiecutter.model_name}}', 'Port {{cookiecutter.model_name}}'])
        _, self._blade_name_template, self._port_name_template = o.get("driver_variable", {}).get("resource_name",
            ['Unused', 'Blade {address}', 'Port {address}'])


        self._example_driver_setting = o.get("driver_variable", {}).get("example_driver_setting", False)

        self._logger.info('Connecting...')
        cli_type = 'tl1'
        self._connection = {{cookiecutter.model_name.replace(' ', '')}}CliConnection(self._logger, cli_type, self._host, self._port, self._username, self._password)
        self._logger.info('Connected')

    def logout(self):
        """
        :return: None
        """
        self._logger.info('Disconnecting...')
        self._cli_connection = None
        self._logger.info('Disconnected')

    def get_resource_description(self, address):
        """
        :param address: str: root address
        :return: L1DriverResourceInfo
        """

        # o1 = self._connection.tl1_command('RTRV-NETYPE:{name}::{counter}:;')
        # o2 = self._connection.tl1_command('RTRV-PATCH:{name}::{counter}:;')
        # self._logger.info('netype: %s' % o1)
        # self._logger.info('patch: %s' % o2)
        # ... parse data

        # o1 = self._connection.show_version()
        # o2 = self._connection.show_interfaces()
        # self._logger.info('version: %s' % o1)
        # self._logger.info('interfaces: %s' % o2)
        # ... parse data

        sw = L1DriverResourceInfo('', address, self._switch_family, self._switch_model, serial='-1')
        sw.set_attribute('Model', 'my model')
        sw.set_attribute('Version', '123')
        sw.set_attribute('Hardware Type', 'my hardware type')
        sw.set_attribute('Vendor', 'my vendor')
        for module in range(3):
            blade = L1DriverResourceInfo(self._blade_name_template.replace('{address}', str(module)),
                                         '%s/%d' % (address, module),  # full address
                                         self._blade_family,
                                         self._blade_model,
                                         serial='-1')
            sw.add_subresource(blade)
            for portaddr in range(5):
                port = L1DriverResourceInfo(
                    self._port_name_template.replace('{address}', str(portaddr)),
                    '%s/%d/%d' % (address, module, portaddr),  # full address
                    self._port_family,
                    self._port_model,
                    map_path='%s/%d/%d' % (address, module, 4-portaddr),
                    serial='-1')
                port.set_attribute('State', 0, typename='Lookup')  # Lookup values must be specified by index
                port.set_attribute('Protocol Type', 0, typename='Lookup')  # Lookup values must be specified by index
                port.set_attribute('Port Description', 'description %d' % portaddr, typename='Lookup')
                blade.add_subresource(port)

        self._logger.info('get_resource_description returning xml: [[[' + sw.to_string() + ']]]')
        return sw

    def map_uni(self, src_port, dst_port):
        """
        :param src_port: str: source port resource full address separated by '/'
        :param dst_port: str: destination port resource full address separated by '/'
        :return: None
        """
        self._logger.info('map_uni {} {}'.format(src_port, dst_port))

        min_port = min(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))
        max_port = max(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))

        # self._connection.tl1_command("ENT-PATCH:{name}:%d,%d:{counter}:;" % (min_port, max_port))
        # self._connection.my_command1(min_port, max_port)

    def map_bidi(self, src_port, dst_port, mapping_group_name):
        """
        :param src_port: str: source port resource full address separated by '/'
        :param dst_port: str: destination port resource full address separated by '/'
        :param mapping_group_name: str
        :return: None
        """
        self._logger.info('map_bidi {} {} group={}'.format(src_port, dst_port, mapping_group_name))

        min_port = min(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))
        max_port = max(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))

        # self._connection.tl1_command("ENT-PATCH:{name}:%d,%d:{counter}:;" % (min_port, max_port))
        # self._connection.my_command2(min_port, max_port)

    def map_clear_to(self, src_port, dst_port):
        """
        :param src_port: str: source port resource full address separated by '/'
        :param dst_port: str: destination port resource full address separated by '/'
        :return: None
        """
        self._logger.info('map_clear_to {} {}'.format(src_port, dst_port))

        min_port = min(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))
        max_port = max(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))

        # self._connection.tl1_command("DLT-PATCH:{name}:%d:{counter}:;" % (min_port))
        # self._connection.my_command3(min_port, max_port)

    def map_clear(self, src_port, dst_port):
        """
        :param src_port: str: source port resource full address separated by '/'
        :param dst_port: str: destination port resource full address separated by '/'
        :return: None
        """
        self._logger.info('map_clear {} {}'.format(src_port, dst_port))

        min_port = min(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))
        max_port = max(int(src_port.split('/')[-1]), int(dst_port.split('/')[-1]))

        # self._connection.tl1_command("DLT-PATCH:{name}:%d:{counter}:;" % (min_port))
        # self._connection.my_command3(min_port, max_port)

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        :param src_port: str: source port resource full address separated by '/'
        :param dst_port: str: destination port resource full address separated by '/'
        :param speed: str
        :param duplex: str
        :return: None
        """
        self._logger.info('set_speed_manual {} {} {} {}'.format(src_port, dst_port, speed, duplex))

    def set_state_id(self, state_id):
        """
        :param state_id: str
        :return: None
        """
        self._logger.info('set_state_id {}'.format(state_id))

    def get_attribute_value(self, address, attribute_name):
        """
        :param address: str
        :param attribute_name: str
        :return: str
        """
        self._logger.info('get_attribute_value {} {} -> "fakevalue"'.format(address, attribute_name))
        return 'fakevalue'

    def get_state_id(self):
        """
        :return: str
        """
        self._logger.info('get_state_id')
        return '-1'

