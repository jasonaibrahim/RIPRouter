from sim.api import *
from sim.basics import *
"""Create your RIP router in this file.
"""
class RIPRouter (Entity):
	default_cost = 1
	updates_sent = 0
	max_hop_count = 100
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
		self.send(packet, self.ports[link][0])

	def discover(self, packet, port):
		""" Upon receiving DiscoveryPacket, call routing table's
		methods to establish new link in Routing Table."""
		direct_link = packet.src
		if packet.is_link_up:
			self.ports[direct_link] = (port,)
			self.routing_table.link_up(direct_link)
		else:
			del self.ports[direct_link]
			self.routing_table.link_down(direct_link)
		self.routing_table.send_best_costs()

	def update(self, packet, port):
		""" Call routing table's update method to update table. Send updates.
		If the table has converged, no further updates are sent."""
		if isinstance(packet.src, Entity):
			self.routing_table.update(packet)

	def forward(self, packet, port):
		""" Send packet to packet's destination if destination reachable."""
		try:
			self.send_packet(packet, packet.dst)
		except KeyError:
			pass

class RoutingTable(object):
	def __init__(self, owner):
		self.owner = owner
		self.costs = {}
		self.best_costs = {}
		self.best_ports = {}
		self.new_min = True

	def link_up(self, node):
		""" When a new link comes up, initialize a new entry in routing table.
		and pass the buck to update_best_costs to get all of the best costs."""
		self.costs[node]= {}
		self.costs[node][node], self.best_costs[node] = 1, 1
		self.best_ports[node] = node
		self.update_best_costs()

	def link_down(self, node):
		""" When a link goes down, we should reset our best costs and
		delete that nodes entry from our routing table. then pass the buck 
		to update to recalculate the best costs."""
		del self.costs[node]
		if isinstance(node, RIPRouter):
			self.best_ports = {}
			self.best_costs = {}
		else:
			del self.best_costs[node]
			del self.best_ports[node]
		self.update_best_costs()

	def update(self, update=None):
		"""Receive update packet from direct link neighbor."""
		src = update.src
		paths = update.paths
		for path in paths.copy():
			if paths[path] >= RIPRouter.max_hop_count:
				del paths[path]
		self.costs[src] = paths
		for path in paths:
			self.costs[src][path] = self.best_costs[src] + paths[path]
		self.costs[src][src] = 1
		self.del_unknown_dests(src)
		self.update_best_costs()
		if self.new_min:
			self.send_best_costs()
		self.new_min = False

	def update_best_costs(self):
		""" To update all of the best_costs we have in order to know
		what our shortest paths are."""
		for link in self.costs:
			for dest in self.costs[link]:
				try:
					if self.costs[link][dest] < self.best_costs[dest]:
						self.best_costs[dest] = self.costs[link][dest]
						self.best_ports[dest] = link
						self.new_min = True
				except KeyError:
					self.best_costs[dest] = self.costs[link][dest]
					self.best_ports[dest] = link
					self.new_min = True

	def del_unknown_dests(self, src, path=None):
		""" To delete any destinations we may have heard from a neighbor in a previous
		update, but did not hear in the current update."""
		for dest in self.best_costs.copy():
			try:
				if dest not in self.costs[src].keys() and self.best_ports[dest] == src:
					del self.best_costs[dest]
					del self.best_ports[dest]
					self.new_min = True
			except KeyError:
				self.best_costs = {}
				self.best_ports = {}
				self.update_best_costs()

	def find_forwarding_port(self, dest):
		return self.best_ports[dest]

	def send_best_costs(self):
		for link in self.costs:
			update = RoutingUpdate()
			for dest in self.best_costs:
				if not self.poison_reverse(dest, link) and link is not dest:
					update.add_destination(dest, self.best_costs[dest])
			self.owner.send_packet(update, link)

		RIPRouter.updates_sent += 1

	def poison_reverse(self, dest, link):
		if dest == link:
			return False
		elif self.best_ports[dest] == link:
			return True
		return False
