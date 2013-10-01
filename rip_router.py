from sim.api import *
from sim.basics import *

"""Create your RIP router in this file.
"""
class RIPRouter (Entity):
	default_cost = 1
	def __init__(self):
		def init_helper():
			self.packet_actions[RoutingUpdate] = self.update
			self.packet_actions[DiscoveryPacket] = self.discover
		self.packet_actions = {}
		self.routing_table = RoutingTable(self)
		self.ports = {}
		init_helper()

	def handle_rx (self, packet, port):
		""" Deal with any type of packet that may come in on a port."""
		try:
			self.packet_actions[type(packet)](packet, port)
		except KeyError:
			if isinstance(packet, Packet):
				self.forward(packet, port)
			else:
				print("Unknown packet.")

	# def hand_off(self, dest):
	# 	"""Return the minimum cost port to get to destination dest"""
	# 	# return self.routing_table.forwarding_port(dest)
	# 	return self.ports[dest]

	def send_updates(self):
		""" Send a neighbor-specific update to each neighbor. Updates 
		are of the type RoutingUpdate and are specific to each neighbor
		mainly for poison reverse."""
		for neighbor in self.routing_table.neighbors:
			update = RoutingUpdate()
			for dest in self.routing_table.destinations:
				min_cost = self.routing_table.minimum(self.table()[dest])
				if dest != neighbor and min_cost != float('inf'):
					update.add_destination(dest, min_cost)
			if update.paths:
				self.send_packet(update, neighbor)

	def send_packet(self, packet, dest):
		""" Send packet to destination. If the packet is only meant
		for other routers, it is not sent to a host. """
		not_for_dest = (isinstance(packet, RoutingUpdate) \
		or isinstance(packet, DiscoveryPacket)) \
		and isinstance(dest, HostEntity)
		if not_for_dest:
			return
		link = self.routing_table.find_forwarding_port(dest)
		self.send(packet, self.ports[link])

	# def table(self):
	# 	""" Return the dictionary in self's RoutingTable."""
	# 	return self.routing_table.t

	def discover(self, packet, port):
		""" Upon receiving DiscoveryPacket, call routing table's
		methods to establish new link in Routing Table."""
		# if packet.is_link_up:
		# 	self.routing_table.init_new_link(packet.src, port)
		# else:
		# 	self.routing_table.take_link_down(packet.src, port)
		# self.send_updates()
		direct_link = packet.src
		self.ports[direct_link] = port
		self.routing_table.link_up(direct_link)


	def update(self, packet, port):
		""" Call routing table's update method to update table. Send updates.
		If the table has converged, no further updates are sent."""
		# if self.routing_table.update(packet, port):
		# 	return
		# self.send_updates()
		# print(packet.paths)
		# pass
		self.routing_table.update(packet)

	def forward(self, packet, port):
		""" Send packet to packet's destination if destination reachable."""
		try:
			self.send_packet(packet, packet.dst)
		except KeyError:
			return


class RoutingTable(object):
	def __init__(self, owner):
		self.owner = owner
		self.direct_links = []
		self.neighbors = []
		self.costs = {}
		self.table = {}
		self.best_costs = {}

	def link_up(self, node):
		self.direct_links.append(node) if node is not self.owner else None
		self.neighbors.append(node) if node not in self.neighbors else None
		self.costs[node]= {}
		self.costs[node][node], self.best_costs[node] = 1, 1
		self.initialization()

	def link_down(self, node):
		self.direct_links.pop(self.direct_links.index(node))
		self.costs[node][node] = float('inf')
		self.update(True)

	def initialization(self):
		for node in self.neighbors:
			if node in self.direct_links:
				self.best_costs[node] = self.costs[node][node]
			else:
				self.best_costs[node] = float('inf')
		self.send_best_costs()

	def update(self, update=None, cost_change=False):
		src = update.src
		paths = update.paths
		if cost_change:
			for dest in paths:
				if dest is not self.owner:
					self.costs[src][dest] = float('inf')
		else:
			for dest in paths:
				if dest not in self.neighbors:
					self.neighbors.append(dest)
					self.best_costs[dest] = float('inf')
					self.update(update)
				self.costs[src][dest] = 1 + paths[dest] 
				if self.costs[src][dest] < self.best_costs[dest]:
					self.best_costs[dest] = self.costs[src][dest]
					self.send_best_costs()

	def find_forwarding_port(self, dest):
		min_val = [float('inf'), None]
		for link in self.costs:
			for path in self.costs[link]:
				if path == dest:
					if self.costs[link][dest] < min_val[0]:
						min_val[0] = self.costs[link][dest]
						min_val[1] = link
		return min_val[1]

	# def calc_best_paths(self):
		
	# 	try:
	# 		changes_made = False
	# 		for node in self.neighbors:
	# 			for dest in self.costs[node]:
	# 				if self.costs[node][dest] <= self.best_costs[dest]:
	# 					self.best_costs[dest] = self.costs[node][dest]
	# 					changes_made = True
	# 		return changes_made
	# 	except KeyError:
	# 		return False

	def send_best_costs(self):
		for link in self.direct_links:
			update = RoutingUpdate()
			for node in self.neighbors:
				update.add_destination(node, self.best_costs[node])
			self.owner.send_packet(update, link)















# class RoutingTable(object):
# 	def __init__(self, owner):
# 		self.owner = owner
# 		self.t = {}
# 		self.neighbors = {}
# 		self.destinations = []

# 	def init_new_link(self, neighbor, port):
# 		"""When a neighboring link goes up, add to destinations 
# 		and neighbors, and add its port with cost to each destination 
# 		as inf."""
# 		self.add_destination(neighbor)
# 		self.add_neighbor(neighbor, port)
# 		for dest in self.t.keys():
# 			for i in range(self.owner.get_port_count()):
# 				try:
# 					self.t[dest][i]
# 				except IndexError:
# 					self.t[dest].insert(i, float('inf'))

# 	def take_link_down(self, neighbor, port):
# 		"""When a neighboring link goes down, we set the cost to get to 
# 		each destination through that neighbor to nil, and delete neighbor
# 		from dictionary."""
# 		for dest in self.t.keys():
# 			self.t[dest][port] = None
# 		del self.neighbors[neighbor]

# 	def update(self, packet, port):
# 		"""Update the routing table upon receiving a RoutingUpdate packet.
# 		Also decide whether or not the table has converged. Method returns
# 		True is table has converged, False otherwise."""
# 		paths = packet.paths
# 		src = packet.src
# 		convergence = False
# 		for path in paths:
# 			if path not in self.destinations:
# 				self.add_destination(path)
# 		for dest in self.destinations:
# 			if dest == src:
# 				pass
# 			elif dest not in paths:
# 				self.t[dest][self.neighbors[src]] = float('inf')
# 				convergence = False
# 			else:
# 				if self.t[dest][self.neighbors[src]] == 1 + paths[dest]:
# 					convergence = True 
# 				else:
# 					self.t[dest][self.neighbors[src]] = 1 + paths[dest]
# 					convergence = False
# 		for dest in src.routing_table.destinations:
# 			if dest not in self.destinations:
# 				self.add_destination(dest)
# 				convergence = False
# 		return convergence

# 	def add_destination(self, dest):
# 		"""Add a new destination to the routing table and set all initial
# 		values of routing via each neighbor to inf."""
# 		self.t[dest] = [float('inf') for i in range(self.owner.get_port_count())]
# 		if dest not in self.destinations:
# 			self.destinations.append(dest)

# 	def add_neighbor(self, neighbor, port):
# 		"""Add neighbor to routing table and set the cost to route
# 		to it to the default one-hop cost."""
# 		self.t[neighbor][port] = self.owner.default_cost
# 		self.neighbors[neighbor] = port

# 	def forwarding_port(self, dest):
# 		"""Return the port number associated with the minimum cost
# 		path to dest"""
# 		return self.t[dest].index(self.minimum(self.t[dest]))

# 	def minimum(self, costs):
# 		"""Given an array of costs, returns the minimum cost. Done this
# 		way because cost array may contain nil values"""
# 		min_val = float('inf')
# 		for cost in costs:
# 			if cost is None:
# 				pass
# 			elif cost < min_val:
# 				min_val = cost
# 		return min_val

# 	def __repr__(self):
# 		s = "[ "
# 		for dest in self.destinations:
# 			s += "d: " + str(dest) + " -->" + str(self.t[dest]) + ", "
# 		s += "]"
# 		return s

