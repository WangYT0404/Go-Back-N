#main0.py

import simpy
from Node1 import Node

env=simpy.Environment()

band_width=200
file_data=50#bit
file_num=1
packet_size=10#bit
window_size=4
timer=0.5#s
sleep_interval=0.02

node0=Node(env,name=0,timer_duration=timer,sleep_interval=sleep_interval,
           band_width=band_width,window_size=window_size,packet_size=packet_size)
node1=Node(env,name=1,timer_duration=timer,sleep_interval=sleep_interval,
           band_width=band_width,window_size=window_size,packet_size=packet_size)
node2=Node(env,name=2,timer_duration=timer,sleep_interval=sleep_interval,
           band_width=band_width,window_size=window_size,packet_size=packet_size)
node3=Node(env,name=3,timer_duration=timer,sleep_interval=sleep_interval,
           band_width=band_width,window_size=window_size,packet_size=packet_size)
nodes=[node0,node1,node2,node3]


env.process(node0.start(start_time=0.4,file_id=0,des_node=node1,nodes=nodes))
env.process(node2.start(start_time=0,file_id=1,des_node=node3,nodes=nodes))
env.process(node0.start(start_time=0.2,file_id=2,des_node=node3,nodes=nodes))
env.run(until=50)


print('node1[',0,']:')
for pkt in node1.packets[0]:
    print(pkt.packet_id)
print('node3[',1,']:')
for pkt in node3.packets[1]:
    print(pkt.packet_id)
print('node3[',2,']:')
for pkt in node3.packets[2]:
    print(pkt.packet_id)