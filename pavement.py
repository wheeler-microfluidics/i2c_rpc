from pprint import pprint
import sys

from paver.easy import task, needs, path, sh, cmdopts, options
from paver.setuputils import setup, find_package_data

import version
sys.path.append(path('.').abspath())
from i2c_rpc import get_sketch_directory, package_path
try:
    from arduino_rpc.proto import CodeGenerator
except ImportError:
    import warnings

    warnings.warn('Could not import `clang`-based code-generator.')


i2c_rpc_files = find_package_data(package='i2c_rpc', where='i2c_rpc',
                                  only_in_packages=False)
pprint(i2c_rpc_files)

PROTO_PREFIX = 'commands'

DEFAULT_ARDUINO_BOARDS = ['uno']

setup(name='wheeler.i2c_rpc',
      version=version.getVersion(),
      description='Arduino RPC node packaged as Python package.',
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='http://github.com/wheeler-microfluidics/i2c_rpc.git',
      license='GPLv2',
      install_requires=['arduino_rpc'],
      packages=['i2c_rpc'],
      package_data=i2c_rpc_files)


@task
def generate_command_code():
    code_generator = CodeGenerator(get_sketch_directory().joinpath('Node.h'),
                                   disable_i2c=getattr(options, 'disable_i2c',
                                                       False))

    definition_str = code_generator.get_protobuf_definitions()
    output_dir = package_path().joinpath('protobuf').abspath()
    output_file = output_dir.joinpath('%s.proto' % PROTO_PREFIX)
    with output_file.open('wb') as output:
        output.write(definition_str)

    header_str = code_generator.get_command_processor_header()
    output_dir = get_sketch_directory()
    output_file = output_dir.joinpath('NodeCommandProcessor.h')
    with output_file.open('wb') as output:
        output.write(header_str)


@task
# Generate protocol buffer request and response definitions, implementing an
# RPC API using the union message pattern suggested in the [`nanopb`][1]
# examples.
#
# [1]: https://code.google.com/p/nanopb/source/browse/examples/using_union_messages/README.txt
@needs('generate_command_code')
def generate_nanopb_code():
    from nanopb_helpers import compile_nanopb

    protobuf_dir = package_path().joinpath('protobuf').abspath()
    for proto_path in protobuf_dir.files('*.proto'):
        prefix = proto_path.namebase
        nanopb = compile_nanopb(proto_path)
        header_name = prefix + '_pb.h'
        source_name = prefix + '_pb.c'
        sketch = get_sketch_directory()
        print 'write `%s` and `%s` to `%s`' % (header_name, source_name,
                                               sketch)
        sketch.joinpath(header_name).write_bytes(nanopb['header'])
        sketch.joinpath(source_name).write_bytes(nanopb['source']
                                                 .replace('{{ header_path }}',
                                                          header_name))


@task
@needs('generate_command_code')
def generate_pb_python_module():
    from nanopb_helpers import compile_pb

    output_dir = package_path().abspath()
    protobuf_dir = package_path().joinpath('protobuf').abspath()
    for proto_path in protobuf_dir.files('*.proto'):
        prefix = proto_path.namebase
        pb = compile_pb(proto_path)
        output_dir.joinpath('protobuf_%s.py' %
                            prefix).write_bytes(pb['python'])


@task
@needs('generate_nanopb_code', 'generate_pb_python_module')
@cmdopts([('sconsflags=', 'f', 'Flags to pass to SCons.'),
          ('boards=', 'b', 'Comma-separated list of board names to compile '
           'for (e.g., `uno`).')])
def build_firmware():
    scons_flags = getattr(options, 'sconsflags', '')
    boards = [b.strip() for b in getattr(options, 'boards', '').split(',')
              if b.strip()]
    if not boards:
        boards = DEFAULT_ARDUINO_BOARDS
    for board in boards:
        # Compile firmware once for each specified board.
        sh('scons %s ARDUINO_BOARD="%s"' % (scons_flags, board))


@task
@needs('generate_setup', 'minilib', 'build_firmware',
       'setuptools.command.sdist')
def sdist():
    """Overrides sdist to make sure that our setup.py is generated."""
    pass
