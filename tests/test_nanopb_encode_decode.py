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

    # Test `int` and `uint` for 8, 16, and 32-bit widths.
    for signedness in ('u', ''):
        for width in (8, 32):
            if not signedness and 8:
                # Skip signed 8-bit integers, since we do not have enough
                # memory on the device to add the method for testing.
                continue
            upper = (1 << width) - 1 if signedness else (1 << (width - 1)) - 1
            values = np.linspace(0, upper, num=100).astype(int)
            for value in values:
                yield (_test_nanopb_encode_echo_integral, signedness, width,
                       i2c_local, remote_address, value)

    values = np.linspace(0, 100)
    for value in values:
        yield (_test_nanopb_encode_echo_float, i2c_local, remote_address,
               value)


def _test_nanopb_encode_echo_integral(signedness, width, board, remote_address,
                                      value):
    method = getattr(board, 'test_nanopb_encode_echo_%sint%d' % (signedness,
                                                                 width))
    eq_(method(address=remote_address, value=value), value)


def _test_nanopb_encode_echo_float(board, remote_address, value):
    np.allclose([board.test_nanopb_encode_echo_float(address=remote_address,
                                                     value=value)], [value])
