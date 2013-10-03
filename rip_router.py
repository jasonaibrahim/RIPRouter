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

	def discover(self, packet, port):
		""" Upon receiving DiscoveryPacket, call routing table's
		methods to establish new link in Routing Table."""
		# if packet.is_link_up:
		# 	self.routing_table.init_new_link(packet.src, port)
		# else:
		# 	self.routing_table.take_link_down(packet.src, port)
		# self.send_updates()
		direct_link = packet.src
		if packet.is_link_up:
			self.ports[direct_link] = port
			self.routing_table.link_up(direct_link)
		else:
			self.routing_table.link_down(packet)
		self.routing_table.update_best_costs()
		self.routing_table.send_best_costs()


	def update(self, packet, port):
		""" Call routing table's update method to update table. Send updates.
		If the table has converged, no further updates are sent."""
		# if self.routing_table.update(packet, port):
		# 	return
		# self.send_updates()
		# print(packet.paths)
		# pass
		# print(self, packet.src, packet.paths)
		self.routing_table.update(packet)

	def forward(self, packet, port):
		""" Send packet to packet's destination if destination reachable."""
		try:
			self.send_packet(packet, packet.dst)
		except KeyError:
			print("Unknown destination. Retry.")
			# Below we deal with attempting to force send an unknown packet by linking
			# to neighbors in order to find out more information about the destination
			# being handed to us.
			# try:
			# 	for link in self.routing_table.direct_links:
			# 		if isinstance(link, RIPRouter):
			# 			self.linkTo(link)	
			# except KeyError:
			# 	return

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

	def link_down(self, packet):
		node = packet.src
		self.direct_links.pop(self.direct_links.index(node))
		for dest in self.costs[node]:
			if self.costs[node][dest] == self.best_costs[dest]:
				self.best_costs[dest] = float('inf')
			self.costs[node][dest] = float('inf')

	def update_best_costs(self):
		for link in self.costs:
			for dest in self.costs[link]:
				if self.costs[link][dest] < self.best_costs[dest]:
					self.best_costs[dest] = self.costs[link][dest]

	def initialization(self):
		for node in self.neighbors:
			if node in self.direct_links:
				self.best_costs[node] = self.costs[node][node]
			else:
				self.best_costs[node] = float('inf')

	def update(self, update=None, cost_change=False):
		src = update.src
		paths = update.paths
		# if cost_change:
		# 	for dest in paths:
		# 		if dest is not self.owner:
		# 			self.costs[src][dest] = float('inf')
		# else:
		for dest in paths:
			if dest not in self.neighbors:
				self.neighbors.append(dest)
				self.best_costs[dest] = float('inf')
				self.update(update)
			# self.costs[src][dest] = 1 + paths[dest] 
			self.costs[src][dest] = self.costs[src][src] + paths[dest]

			if self.costs[src][dest] < self.best_costs[dest]:
				self.best_costs[dest] = self.costs[src][dest]
				self.send_best_costs()
			elif paths[dest] == float('inf'):
				if self.costs[src][dest] == self.best_costs[dest]:
					self.best_costs[dest] = float('inf')
				del self.costs[src][dest]
				self.update_best_costs()
				# self.send_best_costs()

	def find_forwarding_port(self, dest):
		min_val = [float('inf'), None]
		for link in self.costs:
			for path in self.costs[link]:
				if path == dest:
					if self.costs[link][dest] < min_val[0]:
						min_val[0] = self.costs[link][dest]
						min_val[1] = link
		# if min_val[0] == float('inf'):
		# 	self.update_best_costs()
		return min_val[1]

	def send_best_costs(self):
		for link in self.direct_links:
			update = RoutingUpdate()
			for node in self.neighbors:
				if node is not self.owner:
					try:
						if self.costs[link][node] == self.best_costs[node]:
							# print(self.owner, link, node, "poison reverse")
							update.add_destination(node, float('inf'))
						else:
							update.add_destination(node, self.best_costs[node])
					except KeyError:
						update.add_destination(node, self.best_costs[node])
						pass

					# update.add_destination(node, self.best_costs[node])
			# if pr:
				# print(update.paths)
			self.owner.send_packet(update, link)

