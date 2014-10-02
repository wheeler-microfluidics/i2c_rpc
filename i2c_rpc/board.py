from collections import OrderedDict
import time

from nadamq.command_proxy import (NodeProxy, RemoteNodeProxy,
                                  CommandRequestManager,
                                  CommandRequestManagerDebug, SerialStream)
from .requests import (REQUEST_TYPES, CommandResponse, CommandRequest,
                       CommandType)
try:
    from .protobuf_custom import DescriptionStrings
except ImportError:
    # `protobuf_commands.py` must have been generated with an old version of
    # `protoc`, so we have to manually wrap the `_COMMANDTYPE` enum.
    from .protobuf_custom import _DESCRIPTIONSTRINGS

    class DescriptionStrings(object):
        by_name = OrderedDict(sorted([(k, v.number)
                                      for k, v in
                                      _DESCRIPTIONSTRINGS.values_by_name
                                      .items()]))
        by_value = OrderedDict([(v, k) for k, v in by_name.items()])

        @classmethod
        def Name(cls, value):
            return cls.by_value[value]

        @classmethod
        def Value(cls, name):
            return cls.by_name[name]

        @classmethod
        def items(cls):
            return cls.by_name.items()


class I2CBoardMixin(object):
    def description(self):
        return dict([(k, self.description_string(key=v))
                     for k, v in DescriptionStrings.items()])


class I2CBoard(NodeProxy, I2CBoardMixin):
    def __init__(self, port, baudrate=115200, debug=False):
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
        stream = SerialStream(port, baudrate=baudrate)
        super(I2CBoard, self).__init__(request_manager, stream)
        self._stream._serial.setDTR(False)
        time.sleep(0.5)
        self._stream._serial.setDTR(True)
        time.sleep(1)
        print 'free memory:', self.ram_free()


class RemoteI2CBoard(RemoteNodeProxy, I2CBoardMixin):
    def __init__(self, forward_proxy, remote_address, debug=False,
                 timeout=None):
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
        super(RemoteI2CBoard, self).__init__(forward_proxy, remote_address,
                                             request_manager)
