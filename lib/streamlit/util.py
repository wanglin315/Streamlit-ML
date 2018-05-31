# -*- coding: future_fstrings -*-

"""A bunch of useful utilites."""

# flake8: noqa
import uuid
import contextlib
import os
import yaml
import threading

__STREAMLIT_LOCAL_ROOT = '.streamlit'
__CACHE = {}

def __cache(path, serialize, deserialize):
    """Performs two levels of caching:

    1. The data is cached to disk.
    2. The data is memoized future reference.

    Arguments are as follows:

    path - path to save the data
    serialize - serialize to string function
    deserialize - deserialize from string function

    NOTE: The wrapped function must take no arguments!
    """
    def decorator(func):
        cached_value = []
        lock = threading.Lock()
        def wrapped_func():
            with lock:
                if not cached_value:
                    try:
                        with streamlit_read(path) as input:
                            cached_value.append(deserialize(input.read()))
                    except FileNotFoundError:
                        cached_value.append(func())
                        with streamlit_write(path) as output:
                            output.write(serialize(cached_value[0]))
                return cached_value[0]
        return wrapped_func
    return decorator

@__cache('local_uuid.txt', str, uuid.UUID)
def get_local_id():
    """Returns a local id which identifies this user to the database."""
    return uuid.uuid4()

@contextlib.contextmanager
def streamlit_read(path, binary=False):
    f"""Opens a context to read this file relative to the streamlit path.

    For example:

    with read('foo.txt') as foo:
        ...

    opens the file `{__STREAMLIT_LOCAL_ROOT}/foo.txt`

    path   - the path to write to (within the streamlit directory)
    binary - set to True for binary IO
    """
    mode = 'r'
    if binary:
        mode += 'b'
    with open(os.path.join(__STREAMLIT_LOCAL_ROOT, path), mode) as handle:
        yield handle

@contextlib.contextmanager
def streamlit_write(path, binary=False):
    r"""
    Opens a file for writing within the streamlit path, and
    ensuring that the path exists. For example:

        with open_ensuring_path('foo/bar.txt') as bar:
            ...

    opens the file {__STREAMLIT_LOCAL_ROOT}/foo/bar.txt for writing,
    creating any necessary directories along the way.

    path   - the path to write to (within the streamlit directory)
    binary - set to True for binary IO
    """
    mode = 'w'
    if binary:
        mode += 'b'
    path = os.path.join(__STREAMLIT_LOCAL_ROOT, path)
    directory = os.path.split(path)[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    with open(path, mode) as handle:
        yield handle

def escape_markdown(raw_string):
    """Returns a new string which escapes all markdown metacharacters.

    Args
    ----
    raw_string : string
        A string, possibly with markdown metacharacters, e.g. "1 * 2"

    Returns
    -------
    A string with all metacharacters escaped.

    Examples
    --------
    ::
        escape_markdown("1 * 2") -> "1 \* 2"
    """
    metacharacters = ['\\', '*', '-', '=', '`', '!', '#', '|']
    result = raw_string
    for character in metacharacters:
        result = result.replace(character, '\\' + character)
    return result

# def __get_config():
#     """Gets the local config file."""
#     if not __LOCAL_CONFIG:
#         __reload_config()
#     return __LOCAL_CONFIG
#
# def __append_to_config(key, value, comment=None):
#     if key in __LOCAL_CONFIG:
#         raise RuntimeError("Cannot append a key that's already in config.")
#     try:
#         with open(__LOCAL_CONFIG_PATH) as config_stream:
#             config_data = config_stream.read()
#     except FileNotFoundError:
#         config_data = ''
#
#     # Make sure that all nonempty documents end with two newlines.
#     config_data = config_data.strip()
#     if config_data == '':
#         pass
#     else:
#         config_data = config_data + '\n\n'
#
#     # Format the comment.
#     if comment:
#         comment = f'# {comment}\n'
#     else:
#         comment = ''
#
#     # Update the config yaml string and write it out.
#     config_data = f'{config_data}{comment}{key}: {value}\n'
#     with open_ensuring_path(__LOCAL_CONFIG_PATH) as config_stream:
#         config_stream.write(config_data)
#
#     # Reload the configuration.
#     __reload_config()
#
# def __reload_config():
#     """Reloads the config file."""
#     config = __LOCAL_CONFIG
#     config.clear()
#     try:
#         with open(__LOCAL_CONFIG_PATH) as config_stream:
#             config.update(yaml.load(config_stream))
#
#             # Add types where necessary.
#             if 'localId' in config:
#                 config['localId'] = bson.ObjectId(config['localId'])
#     except FileNotFoundError:
#         pass
#     return __LOCAL_CONFIG
