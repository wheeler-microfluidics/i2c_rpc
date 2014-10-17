from nose.tools import eq_
from i2c_rpc.board import I2CBoard
import numpy as np
import serial_device


def test_nanopb_encode_decode():
    port = list(serial_device.get_serial_ports())[0]

    i2c_local = I2CBoard(port=port)
    i2c_devices = np.fromstring(i2c_local.i2c_scan(),
                                dtype=np.uint8).astype(int)
    assert(len(i2c_devices) == 1)
    remote_address = i2c_devices[0]

    values = np.linspace(0, (1 << 31) - 1, num=100).astype(int)
    for v in values:
        yield _test_nanopb_encode_echo_int32, i2c_local, remote_address, v


def _test_nanopb_encode_echo_int32(board, remote_address, value):
    eq_(board.test_nanopb_encode_echo_int32(address=remote_address,
                                            value=value), value)
