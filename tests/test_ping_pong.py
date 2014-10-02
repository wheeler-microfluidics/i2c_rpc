from nose.tools import ok_
from i2c_rpc.board import I2CBoard, RemoteI2CBoard
import numpy as np


def test_ping_pong():
    i2c_mega2560 = I2CBoard(port='/dev/ttyUSB0')
    i2c_uno_remote = RemoteI2CBoard(i2c_mega2560, 0x20, debug=False)

    # Test `float`.
    yield _test_float_ping_pong, i2c_uno_remote

    # Test `int` and `uint` for 8, 16, and 32-bit widths.
    for signedness in ('u', ''):
        for width in (8, 16, 32):
            yield _test_integral_ping_pong, i2c_uno_remote, signedness, width


def _test_float_ping_pong(board):
    values = np.linspace(0, 100)
    ok_(np.allclose(np.array([board.ping_pong_float(value=f)
                              for f in values]), values))


def _test_integral_ping_pong(board, signedness, width):
    upper = (1 << width) - 1 if signedness else (1 << (width - 1)) - 1
    values = np.linspace(0, upper, num=100).astype(int)
    ok_(np.allclose(np.array([getattr(board, 'ping_pong_%sint%d' %
                                      (signedness, width))(value=f)
                              for f in values]), values))
