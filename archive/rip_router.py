from sim.api import *
from sim.basics import *

'''
Create your RIP router in this file.
'''

class CostTable(object):
	one_hop_cost = 1

	def __init__(self, owner):
		self.who = owner
		self.table = {}
		self.ports = {}
		self.destinations = []
		self.neighbors = []
		self.has_table_converged = False

	def link_up(self, src, port):
		self.add_neighbor(src)
		self.add_destination(src)
		self.add_port(src, port)

	def initial_setup(self):
		self.has_table_converged = False
		for dest in self.destinations:
			for neighbor in self.neighbors:
				if dest == neighbor:
					cost = self.one_hop_cost
					# self.link_table(dest, neighbor, cost)
				else:
					cost = float('inf')
				self.link_table(dest, neighbor, cost)

	def link_down(self, src, port):
		self.del_neighbor(src)
		self.del_port(src)
		self.has_table_converged = False

	def minimum_costs(self):
		""" Return a table of the minimum cost to route to each destination
		in self's routing table. The format is a dictionary
		whose key is the destination and whose value is a dictionary
		containing the neighbor with the minimum value to
		that destination and that neighbors routing cost.
		{ dest : {neighbor: min_cost} }"""
		min_table = {}
		for dest in self.destinations:
			values = []
			for neighbor in self.table[dest]:
				values.append(neighbor.values()[0])
			min_table[dest] = self.table[dest][values.index(min(values))]
		return min_table

	def get_routing_cost(self, dest, neighbor):
		"""Return the cost of routing 
			to dest via neighbor"""
		try:
			for n  in self.table[dest]:
				if n.keys()[0] == neighbor:
					return n.values()[0]
		except KeyError:
			return float('inf')

	def handle_unknown_dest(self, dest):
		self.add_destination(dest)
		self.initial_setup()

	# def update_table(self, src, update_table):
	# 	old_table = self.table.copy()
	# 	for dest in update_table:
	# 			if dest not in self.destinations and dest != self.who:
	# 				self.handle_unknown_dest(dest)
	# 				self.update_table(src, update_table)
	# 				self.has_table_converged = False
	# 			elif dest != self.who:
	# 				if self.table[dest][self.index_of(self.table[dest], src)][src] == self.get_routing_cost(src,src) + update_table[dest]:
	# 					self.has_table_converged = True
	# 				else:
	# 					self.has_table_converged = False
	# 					self.table[dest][self.index_of(self.table[dest], src)][src] = self.get_routing_cost(src,src) + update_table[dest]

	def update_table(self, src, paths):
		for dest in paths:
			if dest not in self.destinations:
				self.has_table_converged = False
				self.handle_unknown_dest(dest)
				# self.update_table(src, paths)
			else:
				try:
					if self.table[dest][self.index_of(self.table[dest], src)][src] == 1 + paths[dest]:
						self.has_table_converged = True
					else:
						self.has_table_converged = False
						self.table[dest][self.index_of(self.table[dest], src)][src] = 1 + paths[dest]
				except TypeError:
					pass

		for dest in self.destinations:
			if dest not in paths.keys():
				if dest != src:
					ind = self.index_of(self.table[dest], src)
					if ind:
						self.table[dest].pop(ind)


	def index_of(self, array, neighbor):
		for n in array:
			if n.keys()[0] == neighbor:
				return array.index(n)

	def check_convergence(self, src):
		if self.table == src.table.table:
			self.has_table_converged = True
		else:
			self.has_table_converged = False

	def link_table(self, destination, neighbor, cost):
		d = {neighbor: cost}
		if d not in self.table[destination]:
			self.table[destination].append(d)

	def add_destination(self, dest):
		self.destinations.append(dest)
		self.table[dest] = []

	def add_neighbor(self, neighbor):
		self.neighbors.append(neighbor)

	def del_neighbor(self, neighbor):
		self.neighbors.pop(self.neighbors.index(neighbor))
		self.del_neighbor_from_table(neighbor)

	def del_neighbor_from_table(self, neighbor):
		for dest in self.table.keys():
			for d in self.table[dest]:
				if d.keys()[0] == neighbor and dest != neighbor:
					self.table[dest].pop(self.table[dest].index(d))

	def add_port(self, dest, port):
		self.ports[dest] = port

	def del_port(self, dest):
		del self.ports[dest]

	def get_port(self, dest):
		try:
			return self.ports[dest]
		except KeyError:
			return None

class RIPRouter(Entity):
	def __init__(self):
		self.table = CostTable(self)
		self.paths = {}
		self.update = RoutingUpdate()

	def initial_setup(self):
		self.table.initial_setup()

	def link_up(self, src, port):
		self.table.link_up(src, port)

	def link_down(self, src, port):
		self.table.link_down(src, port)

	def make_paths(self):
		self.paths = {}
		min_cost = self.table.minimum_costs()
		for dest in self.table.destinations:
			try:
				if min_cost[dest].values()[0] != float('inf'):
					self.paths[dest] = min_cost[dest].keys()[0]
			except KeyError:
				pass

	def make_paths2(self):
		self.paths = {}
		min_cost = self.table.minimum_costs()
		for dest in min_cost:
			self.paths[dest] = min_cost[dest].keys()[0]

	def organize_updates(self):
		"""Return an dictionary of the updates to be sent to each neighbor.
		Each update is specific to each neighbor in order to implement
		Poison Reverse. Key is the neighbor, value is the RoutingUpdate."""
		updates = {}
		for neighbor in self.table.neighbors:
			updates[neighbor] = self.make_update2(neighbor)
		self.update = updates

	def make_update2(self, neighbor):
		min_cost = self.table.minimum_costs()
		update = RoutingUpdate()
		for dest in min_cost.keys():
			if min_cost[dest].keys()[0] == neighbor:
				# update.add_destination(dest, float('inf'))
				pass
			else:
				update.add_destination(dest, min_cost[dest].values()[0])
		return update

	def send_update2(self):
		for dest in self.update:
			self.send_packet(self.update[dest], dest)

	def make_update(self):
		min_cost = self.table.minimum_costs()
		for dest in min_cost.keys():
			self.update.add_destination(dest, min_cost[dest].values()[0])

	def send_update(self):
		for dest in self.table.destinations:
			self.send_packet(self.update, dest)

	def send_packet(self, packet, dest=None):
		port = self.get_port(self.forward_to(dest))
		self.send(packet, port)

	def forward_to(self, dest):
		try:
			return self.paths[dest]
		except KeyError:
			return None

	def get_port(self, dest):
		return self.table.get_port(dest)

	def save_port(self, src, port):
		self.table.add_port(src, port)

	def discover(self):
		self.initial_setup()
		self.cleanup()

	def has_table_converged(self):
		return self.table.has_table_converged

	def update_routes(self, packet):
		self.table.update_table(packet.src, packet.paths)
		if not self.has_table_converged():
			self.cleanup()
		self.make_paths2()

	def cleanup(self):
		self.organize_updates()
		self.make_paths2()
		self.send_update2()

	def handle_rx (self, packet, port):
		packet.ttl -= 1
		if isinstance(packet, DiscoveryPacket):
			if packet.is_link_up:
				self.link_up(packet.src, port)
				self.discover()
			else:
				print(self)
				print(packet)
				self.link_down(packet.src, port)
				self.discover()
		elif isinstance(packet, RoutingUpdate):
				self.update_routes(packet)
		elif isinstance(packet, Packet):
			self.send_packet(packet, packet.dst)
		else:
			return None
