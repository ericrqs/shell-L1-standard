import json
import os

import sys

from l1_driver_resource_info import L1DriverResourceInfo
from l1_handler_base import L1HandlerBase


class {{cookiecutter.model_name}}L1Handler(L1HandlerBase):
    
    def __init__(self, logger):
        self._logger = logger

        self._host = None
        self._username = None
        self._password = None

        try:
            with open(os.path.join(os.path.dirname(sys.argv[0]), '{{cookiecutter.project_slug}}_runtime_configuration.json')) as f:
                o = json.loads(f.read())
        except Exception as e:
            self._logger.warn('Failed to read JSON config file: ' + str(e))
            o = {}

        self._port = o.get("common_variable", {}).get("connection_port", 22)
        self._prompt = o.get("common_variable", {}).get("device_prompt", "[0-9a-zA-Z@][0-9a-zA-Z@]*>")

        self._example_driver_setting = o.get("driver_variable", {}).get("example_driver_setting", False)


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

        self._logger.info('Connecting...')
        # ...
        self._logger.info('Connected')

    def logout(self):
        """
        :return: None
        """
        self._logger.info('Disconnecting...')
        # ...
        self._logger.info('Disconnected')

    def get_resource_description(self, address):
        """
        :param address: str
        :return: L1DriverResourceInfo
        """
        SWITCH_FAMILY = '{{cookiecutter.family_name}}'
        SWITCH_MODEL = '{{cookiecutter.model_name}}'
        BLADE_PREFIX = 'module'
        BLADE_FAMILY = '{{cookiecutter.family_name}} Blade'
        BLADE_MODEL = '{{cookiecutter.model_name}} Blade'
        PORT_PREFIX = 'port'
        PORT_FAMILY = '{{cookiecutter.family_name}} Port'
        PORT_MODEL = '{{cookiecutter.model_name}} Port'

        sw = L1DriverResourceInfo('', address, SWITCH_FAMILY, SWITCH_MODEL, serial='-1')


        for module in range(3):
            blade = L1DriverResourceInfo('%s%0.2d' % (BLADE_PREFIX, module),
                                         '%s/%d' % (address, module),
                                         BLADE_FAMILY,
                                         BLADE_MODEL,
                                         serial='-1')
            sw.add_subresource(blade)
            for portaddr in range(5):
                port = L1DriverResourceInfo(
                    '%s%0.2d' % (PORT_PREFIX, portaddr),
                    '%s/%d/%d' % (address, module, portaddr),
                    PORT_FAMILY,
                    PORT_MODEL,
                    map_path='%s/%d/%d' % (address, module, 4-portaddr),
                    serial='-1')
                # port.set_attribute('My Attribute 1', 'xxx', typename='String')
                # port.set_attribute('My Attribute 2', 'yyy', typename='String')
                blade.add_subresource(port)

        self._logger.info('get_resource_description returning xml: [[[' + sw.to_string() + ']]]')
        return sw

    def map_uni(self, src_port, dst_port):
        """
        :param src_port: str
        :param dst_port: str
        :return: None
        """
        self._logger.info('map_uni {} {}'.format(src_port, dst_port))

    def map_bidi(self, src_port, dst_port, mapping_group_name):
        """
        :param src_port: str
        :param dst_port: str
        :param mapping_group_name: str
        :return: None
        """
        self._logger.info('map_bidi {} {} group={}'.format(src_port, dst_port, mapping_group_name))

    def map_clear_to(self, src_port, dst_port):
        """
        :param src_port: str
        :param dst_port: str
        :return: None
        """
        self._logger.info('map_clear_to {} {}'.format(src_port, dst_port))

    def map_clear(self, src_port, dst_port):
        """
        :param src_port: str
        :param dst_port: str
        :return: None
        """
        self._logger.info('map_clear {} {}'.format(src_port, dst_port))

    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """
        :param src_port: str
        :param dst_port: str
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

