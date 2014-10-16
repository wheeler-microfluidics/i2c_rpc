from nose.tools import ok_, eq_
from i2c_rpc.board import I2CBoard, RemoteI2CBoard
import numpy as np
import serial_device


def echo_test():
    port = list(serial_device.get_serial_ports())[0]

    i2c_local = I2CBoard(port=port)
    i2c_devices = np.fromstring(i2c_local.i2c_scan(),
                                dtype=np.uint8).astype(int)
    assert(len(i2c_devices) == 1)
    i2c_remote = RemoteI2CBoard(i2c_local, i2c_devices[0])

    # Test `float`.
    yield _test_echo_float, i2c_remote

    # Test `int` and `uint` for 8, 16, and 32-bit widths.
    for signedness in ('u', ''):
        for width in (8, 16, 32):
            yield _test_echo_integral, i2c_remote, signedness, width

    # Construct a string of characters spanning the range of values
    # representable by a byte.
    msg = np.linspace(0, 255, 10).astype(np.uint8).tostring()
    yield _test_echo_str, i2c_remote, msg

    # Construct a string of characters spanning the range of values
    # representable by a byte in reverse order, ending with a zero.
    msg = np.linspace(0, 255, 10).astype(np.uint8).tostring()
    yield _test_echo_str, i2c_remote, msg


def _test_echo_float(board):
    values = np.linspace(0, 100)
    ok_(np.allclose(np.array([board.echo_float(value=f)
                              for f in values]), values))


def _test_echo_integral(board, signedness, width):
    upper = (1 << width) - 1 if signedness else (1 << (width - 1)) - 1
    values = np.linspace(0, upper, num=100).astype(int)
    ok_(np.allclose(np.array([getattr(board, 'echo_%sint%d' %
                                      (signedness, width))(value=f)
                              for f in values]), values))


def _test_echo_str(board, msg):
    eq_(msg, board.echo_str(msg=msg))
