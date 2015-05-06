"""Provides helper functions for interactive prompts

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

from pyexperiment import state
from pyexperiment import conf


def embed_interactive(**kwargs):
    """Embed an interactive terminal into a running python process
    """
    if 'state' not in kwargs:
        kwargs['state'] = state
    if 'conf' not in kwargs:
        kwargs['conf'] = conf

    try:
        import IPython
        ipython_config = IPython.Config()
        ipython_config.TerminalInteractiveShell.confirm_exit = False
        if int(IPython.__version__.split(".")[0]) < 3:
            IPython.embed(config=ipython_config,
                          banner1='',
                          user_ns=kwargs)
        else:
            IPython.embed(config=ipython_config,
                          banner1='',
                          local_ns=kwargs)
    except ImportError:
        import readline  # pylint: disable=unused-variable
        import code

        code.InteractiveConsole(kwargs).interact()
