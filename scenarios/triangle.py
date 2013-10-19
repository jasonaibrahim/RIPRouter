import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub

def create (switch_type = Hub, host_type = BasicHost, n =  5):
    """
    Creates octagonal topology as in the extra credit.
    """

    switches = []
    hosts = []
    for i in range(1, 4):
      s = switch_type.create('s' + str(i))
      switches.append(s)
      h = host_type.create('h' + str(i))
      hosts.append(h)

    hosts[0].linkTo(switches[0])
    switches[0].linkTo(switches[1])
    switches[0].linkTo(switches[2])
    switches[1].linkTo(switches[2])
    hosts[1].linkTo(switches[1])
    hosts[2].linkTo(switches[2])




