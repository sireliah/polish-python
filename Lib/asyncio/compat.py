"""Compatibility helpers dla the different Python versions."""

zaimportuj sys

PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)


def flatten_list_bytes(list_of_data):
    """Concatenate a sequence of bytes-like objects."""
    jeżeli nie PY34:
        # On Python 3.3 oraz older, bytes.join() doesn't handle
        # memoryview.
        list_of_data = (
            bytes(data) jeżeli isinstance(data, memoryview) inaczej data
            dla data w list_of_data)
    zwróć b''.join(list_of_data)
