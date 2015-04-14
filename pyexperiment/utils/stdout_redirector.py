"""Context to redirect stdout (inspired by a tutorial by Eli Bendersky)

Adapted by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from contextlib import contextmanager
import sys


@contextmanager
def stdout_redirector(stream):
    """Redirects standard out to a buffer
    """
    old_stdout = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = old_stdout


@contextmanager
def stdout_err_redirector(stream_out, stream_err):
    """Redirect standard out and err to a buffer
    """
    old_stdout = sys.stdout
    sys.stdout = stream_out
    old_stderr = sys.stderr
    sys.stderr = stream_err
    try:
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
