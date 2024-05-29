# Node.py

import random
from Packet import Packet

drop_prob = 8  # packet loss probability

class Node:
    def __init__(self, env, name, timer, sleep_interval, band_width, window_size, packet_size):
        self.env = env
        self.name = name
        self.band_width = band_width

        self.base_set = {}  # Only for source node, base of the window
        self.next_to_send_set = {}  # Only for source node, next packet to send
        self.timer = timer
        self.timer_set = {}  # Only for source node, base of the window
        self.sleep_interval = sleep_interval
        self.window_size = window_size
        self.window = None  # Only for source node
        self.packet_size = packet_size
        self.packets = {}  # If source node, file_name: packets[]
        self.success_set = {}
        self.num_packets = {}

        self.expected_num_set = {}  # Only for destination node


    def source_send(self, data, start_time, file_id, des_node, nodes):
        yield self.env.timeout(start_time)

        self.packets[file_id] = []
        self.success_set[file_id] = 'Fail'
        seq_num = 0
        offset = 0
        des_name = des_node.name
        while offset < len(data):
            chunk = data[offset:offset + self.packet_size]
            packet = Packet(file_id=file_id, packet_id=seq_num, start_time=start_time, source_now=self.name,
                            destination_now=des_name,
                            source_global=self.name, destination_global=des_name, data=chunk)
            self.packets[file_id].append(packet)
            seq_num += 1
            offset += self.packet_size

        self.num_packets[file_id] = len(self.packets[file_id])
        print('Node', self.name, ' gots —— file_id: ', file_id, ', packets_num: ', self.num_packets[file_id])
        self.base_set[file_id] = 0
        self.next_to_send_set[file_id] = 0
        self.window = self.set_window_size(file_id)

        delay = self.packet_size / self.band_width
        while self.next_to_send_set[file_id] < self.base_set[file_id] + self.window and self.next_to_send_set[file_id] < self.num_packets[file_id]:
            pkt = self.packets[file_id][self.next_to_send_set[file_id]]
            self.env.process(self.send(pkt, delay, des_node, nodes))
            self.next_to_send_set[file_id] += 1

        if file_id not in self.timer_set.keys() or self.timer_set[file_id] == 'Stop':
            self.timer_set[file_id] = 'Running'
            self.env.process(self.start_timer(start_time, file_id, des_name, des_node, nodes))


    def start_timer(self, start_time, file_id, des_name, des_node, nodes):
        yield self.env.timeout(self.timer)
        if self.success_set[file_id] == 'Fail':
            print('Timeout')
            self.next_to_send_set[file_id] = self.base_set[file_id]

            delay = self.packet_size / self.band_width
            while self.next_to_send_set[file_id] < self.base_set[file_id] + self.window and self.next_to_send_set[file_id] < self.num_packets[file_id]:
                pkt = self.packets[file_id][self.next_to_send_set[file_id]]
                self.env.process(self.send(pkt, delay, des_node, nodes))
                self.next_to_send_set[file_id] += 1

            self.env.process(self.start_timer(start_time, file_id, des_name, des_node, nodes))


    def source_receive(self, packet, nodes):
        yield self.env.timeout(0)
        ack = packet.packet_id
        file_id = packet.file_id
        print('Node', self.name, 'got ACK ', ack)
        if ack >= self.base_set[file_id]:
            self.base_set[file_id] = ack + 1
            print('Base updated', self.base_set[file_id])
            self.timer_set[file_id] = 'Stop'

            if self.base_set[file_id] >= self.num_packets[file_id]:
                print('!!!!!!!!!!!!!!!!!!!!file_id:', file_id, 'Transmission Complete')
                self.success_set[file_id] = 'Success'
                return

            self.window = self.set_window_size(file_id)
            delay = self.packet_size / self.band_width
            while self.next_to_send_set[file_id] < self.base_set[file_id] + self.window and self.next_to_send_set[file_id] < self.num_packets[file_id]:
                pkt = self.packets[file_id][self.next_to_send_set[file_id]]
                des_node = nodes[packet.destination_global]
                self.env.process(self.send(pkt, delay, des_node, nodes))
                self.next_to_send_set[file_id] += 1


    def set_window_size(self, file_id):
        base = self.base_set[file_id]
        return min(self.window_size, self.num_packets[file_id] - base)


    def destination_receive(self, packet, nodes):
        yield self.env.timeout(0)
        seq_num = packet.packet_id
        print('Node', self.name, 'receives packet —— file_id: ', packet.file_id, ', packet_id: ', seq_num)
        if packet.file_id not in self.packets.keys():
            self.expected_num_set[packet.file_id] = 0

        if seq_num is not None:
            if seq_num == self.expected_num_set[packet.file_id]:
                print('Node', self.name, 'Got expected packet, Sending ACK', self.expected_num_set[packet.file_id])
                if packet.file_id in self.packets.keys():
                    self.packets[packet.file_id].append(packet)
                else:
                    self.packets[packet.file_id] = [packet]

                packet_ack = Packet(file_id=packet.file_id, packet_id=self.expected_num_set[packet.file_id], start_time=packet.start_time,
                                    source_now=self.name, destination_now=packet.source_global,
                                    source_global=packet.source_global, destination_global=packet.destination_global,
                                    data=None)
                delay = 0.01
                des_node = nodes[packet_ack.destination_now]
                self.expected_num_set[packet.file_id] += 1
                self.env.process(self.send(packet_ack, delay, des_node, nodes))

            else:
                print('Node', self.name, 'Not Got expected packet, Sending ACK', self.expected_num_set[packet.file_id] - 1)
                packet_ack = Packet(file_id=packet.file_id, packet_id=self.expected_num_set[packet.file_id] - 1, start_time=packet.start_time,
                                    source_now=self.name, destination_now=packet.source_global,
                                    source_global=packet.source_global, destination_global=packet.destination_global,
                                    data=None)
                delay = 0.01
                des_node = nodes[packet_ack.destination_now]
                self.env.process(self.send(packet_ack, delay, des_node, nodes))


    def send(self, packet, delay, des_node, nodes):
        print('Node', self.name, 'sending packet —— file_id: ', packet.file_id, ', packet_id: ', packet.packet_id)
        if random.randint(0, drop_prob) > 0:
            yield self.env.timeout(delay)
            self.env.process(des_node.recv(packet, nodes))


    def recv(self, packet, nodes):
        yield self.env.timeout(0)
        if self.name == packet.destination_global:
            self.env.process(self.destination_receive(packet, nodes))
        if self.name == packet.source_global:
            self.env.process(self.source_receive(packet, nodes))
