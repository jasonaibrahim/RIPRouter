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
			self.packet_actions[Packet] = self.forward
		self.packet_actions = {}
		self.routing_table = RoutingTable(self)
		init_helper()

	def handle_rx (self, packet, port):
		try:
			self.packet_actions[type(packet)](packet, port)
		except KeyError:
			return 

	def hand_off(self, dest):
		"""Return the minimum cost port to get to destination dest"""
		return self.routing_table.forwarding_port(dest)

	def send_updates(self):
		for neighbor in self.routing_table.neighbors:
			update = RoutingUpdate()
			for dest in self.routing_table.destinations:
				if self.table()[dest].index(self.routing_table.minimum(self.table()[dest])) == self.routing_table.neighbors[neighbor]:
					min_cost = float('inf')
				else:
					min_cost = self.routing_table.minimum(self.table()[dest])
				if dest != neighbor and min_cost != float('inf'):
					update.add_destination(dest, min_cost)
			if update.paths:
				print(neighbor, update.paths)
				self.send_packet(update, neighbor)

	def send_packet(self, packet, dest):
		self.send(packet, self.hand_off(dest))

	def table(self):
		return self.routing_table.t

	def discover(self, packet, port):
		print("Got a DiscoveryPacket")
		if packet.is_link_up:
			self.routing_table.init_new_link(packet.src, port)
		else:
			self.routing_table.take_link_down(packet.src, port)
		self.send_updates()

	def update(self, packet, port):
		print("Got a Routing Update")

	def forward(self, packet, port):
		print("Got a packet to forward")

class RoutingTable(object):
	def __init__(self, owner):
		self.owner = owner
		self.t = {}
		self.neighbors = {}
		self.destinations = []

	def init_new_link(self, neighbor, port):
		self.add_destination(neighbor)
		self.add_neighbor(neighbor, port)
		for dest in self.t.keys():
			for i in range(self.owner.get_port_count()):
				try:
					self.t[dest][i]
				except IndexError:
					self.t[dest].insert(i, float('inf'))

	def take_link_down(self, neighbor, port):
		for dest in self.t.keys():
			self.t[dest][port] = None
		del self.neighbors[neighbor]

	def add_destination(self, dest):
		self.t[dest] = [float('inf') for i in range(self.owner.get_port_count())]
		if dest not  in self.destinations:
			self.destinations.append(dest)

	def add_neighbor(self, neighbor, port):
		self.t[neighbor][port] = self.owner.default_cost
		self.neighbors[neighbor] = port

	def forwarding_port(self, dest):
		"""Return the port number associated with the minimum cost
		path to dest"""
		return self.t[dest].index(self.minimum(self.t[dest]))

	def minimum(self, costs):
		min_val = float('inf')
		for cost in costs:
			if cost is None:
				pass
			elif cost < min_val:
				min_val = cost
		return min_val

	def __repr__(self):
		s = "[ "
		for dest in self.destinations:
			s += "d: " + str(dest) + " -->" + str(self.t[dest]) + ", "
		s += "]"
		return s
			
class Neighbor(object):
	def __init__(self, name, port):
		self.name = name
		self.port = port
		self.destinations = {}

	def __repr__(self):
		return str(self.name) + " --> " + str(self.destinations)

