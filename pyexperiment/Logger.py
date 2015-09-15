"""Provides a multiprocessing-safe logger with colored console output,
rotating log files, and easy block-timing based on the logging module.

Logging made easy. Just use the module level functions debug, warning,
info etc. to log messages. At some point, preferably at the start of
your program, call init_main to initialize the logger and choose at
which level you want to log to the console and or rotating log files.

Timing made easy. Just use the module level function timed in a 'with'
block to log timing of the code in the block. You can also get a
summary with statistics of all your timed blocks by calling
print_timings.

Written by Peter Duerr, inspired by zzzeek's and airmind's examples on
Stackoverflow (http://stackoverflow.com/a/894284/2481888,
http://stackoverflow.com/a/384125/2481888).

"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import

import logging
import logging.handlers
import copy

import os
import numpy as np

from collections import OrderedDict
from datetime import datetime
from contextlib import contextmanager

from pyexperiment.utils.Singleton import Singleton
from pyexperiment.utils.Singleton import DefaultSingleton
from pyexperiment.utils.DelegateCall import DelegateCall

from pyexperiment.utils import printers


CONSOLE_FORMAT = ("[%(levelname)-19s] [%(relativeCreated)s]"
                  " $BOLD%(message)s$RESET")
"""The format used for logging to the console
"""

FILE_FORMAT_STD_MSG_LEN = 50
"""How much space should be reserved for a normal message in the log
file.
"""

FILE_FORMAT = ("[%(relativeCreated)10.5fs] [%(levelname)-1s]"
               " %(message)-50s (%(filename)s:%(lineno)d) %(processName)s "
               "- %(threadName)s")
"""The format used for logging to file
"""

CONSOLE_STREAM_HANDLER = logging.StreamHandler()
"""The stream handler for the console (can be mocked for testing)
"""


class ColorFormatter(logging.Formatter):
    """Formats logged messages with optional added color for the log level
    """
    def __init__(self, msg, use_color=True):
        """Initializer
        """
        super(ColorFormatter, self).__init__(msg)
        self.use_color = use_color
        self.log_no = 0
        self.colors = self._setup_log_level_colors()

    @staticmethod
    def _setup_log_level_colors():
        """Returns a dictionary with the colors associated to each log level.
        """
        return {'WARNING': printers.COLORS['magenta'],
                'INFO': printers.COLORS['white'],
                'DEBUG': printers.COLORS['blue'],
                'CRITICAL': printers.COLORS['yellow'],
                'ERROR': printers.COLORS['red']}

    def format(self, record):
        """Format the log
        """
        levelname = record.levelname
        if self.use_color and levelname in self.colors:
            levelname_color = printers.colorize(levelname,
                                                self.colors[levelname])

            relative_color = ("%0.3fs" % (record.relativeCreated / 1000.0))
            self.log_no += 1
            record = copy.copy(record)
            record.levelname = levelname_color
            record.relativeCreated = relative_color
            return logging.Formatter.format(self, record)
        else:
            levelname_short = levelname[0]
            relative_s = record.relativeCreated / 1000.0
            record = copy.copy(record)
            record.levelname = levelname_short
            record.relativeCreated = relative_s
            return logging.Formatter.format(self, record)


class MPRotLogHandler(logging.Handler):
    """Multiprocessing-safe handler for rotating log files
    """
    def __init__(self,
                 filename,
                 level=logging.DEBUG,
                 no_backups=0):
        """Initializer
        """
        # Init base class
        super(MPRotLogHandler, self).__init__(level=level)

        # Check if we need to roll_over later
        roll_over_file = os.path.isfile(filename)

        # Prepare the formatter
        file_formatter = ColorFormatter(
            FILE_FORMAT, False)
        # Setup the actual handler for the log files
        self._file_handler = logging.handlers.RotatingFileHandler(
            filename=filename,
            backupCount=no_backups)
        self._file_handler.setLevel(level)
        self.setFormatter(file_formatter)

        if roll_over_file:
            self._file_handler.doRollover()

        # Emit messages in the main process
        self._delegate_emit = DelegateCall(self._file_handler.emit)

    def setFormatter(self, formatter):
        """Overload the setFormatter method"""
        super(MPRotLogHandler, self).setFormatter(formatter)
        self._file_handler.setFormatter(formatter)

    def close(self):
        self._delegate_emit.join()
        self._file_handler.close()
        super(MPRotLogHandler, self).close()

    def _serializable_record(self, record):
        """Ensures that exc_info and args are serializable by converting
        everything to a string.
        """
        if record.name:
            record.name = str(record.name)
        if record.args:
            record.msg = record.msg % record.args
            record.args = None
        if record.exc_info:
            record.exc_text = self.format(record)
            record.exc_info = None

        return record

    def emit(self, record):
        """Emits logged message by delegating it
        """
        try:
            formated = self._serializable_record(record)
            self._delegate_emit(formated)
        except (KeyboardInterrupt, SystemExit):
            raise
        # This should really catch every other exception!
        except Exception:  # pylint: disable=broad-except
            self.handleError(record)


class PreInitLogHandler(logging.Handler, Singleton):
    """Handles messages before the main logger is initialized.
    """
    def __init__(self):
        """Initializer
        """
        self.pre_init_logs = []
        super(PreInitLogHandler, self).__init__()

    def emit(self, msg):
        """Catch logs and store them for later
        """
        # print msg
        self.pre_init_logs.append(msg)


class Logger(logging.Logger, DefaultSingleton):
    """Implements a multiprocessing-safe logger with timing and colored console
    output.
    """
    def __init__(self,
                 console_level=logging.INFO,
                 filename=None,
                 file_level=logging.DEBUG,
                 no_backups=5):
        """Initializer
        """
        # Initialize the base class, the minimal level makes sure no
        # logs are missed
        super(Logger, self).__init__(
            self,
            level=min(console_level, file_level))

        # Setup console logging
        def expand_format_tags(message, use_color=True):
            """Expands $*SEQ tags in a string. If use_color is False, removes
            the tags.
            """
            if use_color:
                message = message.replace(
                    "$RESET",
                    printers.RESET_SEQ).replace("$BOLD",
                                                printers.COLORS['bold'])
            else:
                message = message.replace("$RESET", "").replace("$BOLD", "")
            return message

        color_formatter = ColorFormatter(
            expand_format_tags(CONSOLE_FORMAT, True))

        console_handler = CONSOLE_STREAM_HANDLER
        console_handler.setLevel(console_level)
        console_handler.setFormatter(color_formatter)
        self.addHandler(console_handler)

        # If needed add file handler
        if filename is not None:
            self.addHandler(MPRotLogHandler(filename=filename,
                                            level=file_level,
                                            no_backups=no_backups))

        # Emit the messages saved by the pre-init logger
        for logg in PreInitLogHandler.get_instance().pre_init_logs:
            for handler in self.handlers:
                if logg.levelno >= handler.level:
                    handler.emit(logg)
        PreInitLogHandler.reset_instance()

    def close(self):
        """Close the logger
        """
        for handler in self.handlers:
            handler.close()
        Logger.reset_instance()

    @classmethod
    def _get_pseudo_instance(cls):
        """Return logger that stores the logged messages for later use
        """
        temp_logger = logging.getLogger('pre_init_logger')
        for handler in temp_logger.handlers:
            temp_logger.removeHandler(handler)

        temp_logger.addHandler(PreInitLogHandler.get_instance())
        temp_logger.setLevel(1)
        # temp_logger.debug(
        #     "Using temporary pre-init logger")
        temp_logger.reset_instance = Logger.reset_instance
        temp_logger.close = lambda: None

        return temp_logger


class TimingLogger(Logger):
    """Provides a logger with a `timed` context.

    Calling code in the `timed` context will collect execution timing
    statistics.

    """
    def __init__(self,
                 console_level=logging.INFO,
                 filename=None,
                 file_level=logging.DEBUG,
                 no_backups=5):
        """Initializer

        Creates a logger that logs messages at or above the console_level
        (by default logging.INFO) to stderr. If a filename is given,
        messages at or above the file level (by default logging.DEBUG)
        will be logged to the file with the specified name. If no_backups
        is larger than 0, the file will be rotated at every call of init.
        """
        # Container and aggregator for the timings
        self.timings = OrderedDict()
        self._delegate_process_timings = DelegateCall(self._process_timings)
        super(TimingLogger, self).__init__(console_level,
                                           filename,
                                           file_level,
                                           no_backups)

    @contextmanager
    def timed(self, msg='', level=logging.DEBUG, save_result=True):
        """Timer to be used in a with block. If the level is not None, logs
        the timing at the specified level. If save_result is True,
        captures the result in the timings dictionary.
        """
        # At the start of the with block
        start = datetime.now()
        yield
        # After leaving the with block
        stop = datetime.now()
        elapsed_time = (stop - start).total_seconds()

        # Log if necessary
        if level is not None:
            self.log(level,
                     msg + " took %0.6fs" % elapsed_time)

        # Save result if necessary
        if save_result:
            self._delegate_process_timings((msg, elapsed_time))

    def print_timings(self):
        """Prints a summary of the timings collected with 'timed'.
        """
        # Make sure the delegated calls are done
        self._delegate_process_timings.join()

        if len(self.timings.items()) > 0:
            # Announce timings
            printers.print_blue(  # pylint: disable=no-member
                "Timing Summary:")

            # Iterate over all saved timings
            for msg, times in self.timings.items():
                no_timings = len(times)
                if no_timings > 1:
                    times_array = np.array(times)
                    message = ("\t'%s' (timed %d times): "
                               "total = %0.6fs, "
                               "min = %0.6fs, max = %0.6fs, median = %0.6fs"
                               % (msg,
                                  no_timings,
                                  np.sum(times_array),
                                  np.min(times_array),
                                  np.max(times_array),
                                  np.median(times_array)))
                else:
                    message = "\t'%s': %0.6fs" % (msg, times[0])

                print(message)
        else:
            printers.print_blue(  # pylint: disable=no-member
                "No timings stored...")

    def _process_timings(self, data):
        """Aggregates the timing data in the dict
        """
        # Destructure the data
        msg, elapsed_time = data

        # Save the result
        if msg not in self.timings:
            self.timings[msg] = [elapsed_time]
        else:
            self.timings[msg].append(elapsed_time)

    def close(self):
        """Make sure the delegated calls are all done...
        """
        self._delegate_process_timings.join()
        super(TimingLogger, self).close()
