import time

import numpy as np
from nadamq.command_proxy import (NodeProxy, CommandRequestManager,
                                  CommandRequestManagerDebug, SerialStream)
from serial_device import get_serial_ports
from .requests import (REQUEST_TYPES, CommandResponse, CommandRequest,
                       CommandType)
from .protobuf_custom import DescriptionStrings


class I2CBoard(object):
    def __init__(self, auto_connect=False, port=None, baudrate=115200,
                 timeout=None):
        self._board = None
        self._connected = False
        self._auto_amplifier_gain_initialized = False
        if auto_connect:
            self.connect(port=port, baudrate=baudrate, timeout=timeout)

    def connect(self, port=None, baudrate=115200, debug=False, timeout=None):
        # Attempt to connect to the board.  If no port was specified, try each
        # available serial port until a successful connection is established.
        self._board = None
        if not debug:
            request_manager = CommandRequestManager(REQUEST_TYPES,
                                                    CommandRequest,
                                                    CommandResponse,
                                                    CommandType)
        else:
            request_manager = CommandRequestManagerDebug(REQUEST_TYPES,
                                                         CommandRequest,
                                                         CommandResponse,
                                                         CommandType)
        if port is not None:
            ports = [port]
        else:
            ports = get_serial_ports()
        for port in ports:
            stream = SerialStream(port, baudrate=baudrate)
            if timeout is not None:
                proxy = NodeProxy(request_manager, stream, timeout=timeout)
            else:
                proxy = NodeProxy(request_manager, stream)
            stream._serial.setDTR(False)
            time.sleep(.2)
            stream._serial.setDTR(True)
            time.sleep(1.0)
            if self._test_connection(proxy):
                break
        if not self.connected:
            raise IOError('Could not connect to control board.')
        self.calibration = self.create_feedback_calibration()
        #self._auto_amplifier_gain_initialized = False

    def _test_connection(self, proxy):
        try:
            proxy.ram_free()
            self._board = proxy
            self._connected = True
        except:
            self._connected = False
        return self.connected

    @property
    def port(self):
        return self.board._stream._serial.port

    @property
    def baudrate(self):
        return self.board._stream._serial.baudrate

    @property
    def board(self):
        return self._board

    @property
    def connected(self):
        return self._connected

    def description(self):
        return dict([(k, self.board.description_string(key=v))
                     for k, v in DescriptionStrings.items()])

    def i2c_scan(self):
        return np.fromstring(self.board.i2c_scan(), dtype=np.uint8).tolist()
