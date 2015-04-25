There is no shortage of great Python libraries for command line
interfaces, logging, configuration file management, persistent state, or
plotting. When writing small scripts for quick experiments though, it's
often too much effort to configure these components, and one ends up
rewriting the same setup code over and over again.

Pyexperiment fixes this by providing a very simple way to jump start a
short experiment, adding many features of a full-blown framework.

Importing one or several modules from pyexperiment will give you:

-  A basic *command line interface* that allows calling arbitrary
   functions (and passing arguments) from the command prompt, providing
   help text derived from the functions' docstrings (based on the
   standard library's argparse).
-  A simple *configuration management* with an easy way to provide
   default values (based on the excellent configobj library).
-  A thread-safe *logger* with configurable logging levels, *timing
   utilities* with statistics, and rotating log files (based on the
   standard library's logging module).
-  *Persistent state* with platform independent, configurable,
   (optionally rotating) state files that are compatible with many other
   programs (based on h5py).
-  A sensible setup for *plotting* with configurable defaults (based on
   matplotlib).
-  Many other bits and pieces that might come in handy...

As a design principle, pyexperiment's components come ready to use
without any further configuration. Inevitably then, the choices made in
this setup are opinionated and may or may not fit your personal taste.
Feel free to start a discussion on the
`issues <https://github.com/duerrp/pyexperiment/issues>`__ page.

For usage examples, check the
`examples <https://github.com/duerrp/pyexperiment/tree/master/examples>`__
folder.
