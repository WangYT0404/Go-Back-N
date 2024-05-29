# Packet.py

class Packet:
    def __init__(self,file_id,packet_id,start_time,source_now,destination_now,
                 source_global,destination_global,data):
        self.file_id=file_id
        self.packet_id =packet_id
        self.start_time=start_time

        self.source_now=source_now
        self.destination_now=destination_now

        self.source_global=source_global
        self.destination_global=destination_global

        self.data=data
