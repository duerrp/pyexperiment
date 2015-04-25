"""Provides helper functions for interactive prompts

Written by Peter Duerr
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import


def embed_interactive():
    """Embed an interactive terminal into a running python process
    """
    try:
        import IPython
        ipython_config = IPython.Config()
        ipython_config.TerminalInteractiveShell.confirm_exit = False
        IPython.embed(config=ipython_config,
                      banner1='')
    except ImportError:
        import readline  # pylint: disable=unused-variable
        import code
        variables = globals().copy()
        variables.update(locals())
        code.InteractiveConsole(variables).interact()
