import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub

def create (switch_type = Hub, host_type = BasicHost, n =  15):
    """
    Creates octagonal topology as in the extra credit.
    """

    switches = []
    for i in range(1, n+1):
      s = switch_type.create('s' + str(i))
      switches.append(s)
      h = host_type.create('h' + str(i))
      s.linkTo(h)

    # Connect the switches
    prev = switches[0]
    for s in switches[1:]:
      prev.linkTo(s)
      prev = s
    switches[-1].linkTo(switches[0])

    switches.append(switch_type.create('s' + str(len(switches)+1)))

    prev = switches[0]
    for s in switches[1:]:
      prev.linkTo(switches[-1])
      prev = s


