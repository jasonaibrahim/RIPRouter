import sim
from sim.core import CreateEntity, topoOf
from sim.basics import BasicHost
from hub import Hub

def create (switch_type = Hub, host_type = BasicHost, n =  20):
    """
    Creates a really simple topology like:
    s1 -- s2 -- .. -- sn
     |     |           |
    h1    h2          hn
    n defaults to 2.
    """

    switches = []
    hosts = []
    for i in range(1, n+1):
      s = switch_type.create('s' + str(i))
      switches.append(s)
      h = host_type.create('h' + str(i))
      hosts.append(h)
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


