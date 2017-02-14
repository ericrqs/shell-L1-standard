# CloudShell L1 main
#
# It should not be necessary to edit this file.
#
# This file will be the entry point of Zlitest5.exe
#
# It will be invoked by CloudShell as Zlitest5.exe <listening port number>

from cloudshell.core.logger.qs_logger import get_qs_logger
from l1_driver import L1Driver
from zlitest5_l1_handler import Zlitest5L1Handler
import os
import sys


# LOG_PATH required for qs_logger startup
os.environ['LOG_PATH'] = os.path.join(os.path.dirname(sys.argv[0]), '..', 'Logs')

logger = get_qs_logger(log_group='Zlitest5',
                       log_file_prefix='Zlitest5',
                       log_category='INTERNAL')


# Instantiate your implementation of L1HandlerBase
handler = Zlitest5L1Handler(logger=logger)

# Instantiate standard L1 driver
driver = L1Driver(listen_port=int(sys.argv[1]), handler=handler, logger=logger)

# Listen for commands forever - never returns
driver.go()
