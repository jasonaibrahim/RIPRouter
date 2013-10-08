#!/usr/bin/env python

import sys
import time
import sim

_ENABLE_GUI = "--gui" in sys.argv

# If you don't want to see log messages on the console, uncomment the
# following line.  You might want to do this if you are using the GUI
# which displays logs itself.
_DISABLE_CONSOLE_LOG = True

from rip_router import RIPRouter as switch
from rip_router import RIPRouter

import sim.core
import scenarios

time.sleep(1) # Wait a sec for log client to maybe connect

import scenarios.octagon as scenario

# Import some stuff to use from the interpreter
import sim.basics as basics
import sim.api as api
import sim.topo as topo

import logging
# There are two loggers: one that has output from the simulator, and one
# that has output from you (simlog and userlog respectively).  These are
# Python logger objects, and you can configure them as you see fit.  See
# http://docs.python.org/library/logging.html for info.
api.simlog.setLevel(logging.DEBUG)
api.userlog.setLevel(logging.DEBUG)

total = len(sys.argv)
cmdargs = int(sys.argv[1])

scenario.create(switch_type = switch, n = cmdargs)
start = sim.core.simulate

start()
time.sleep(10)
print(RIPRouter.updates_sent)

