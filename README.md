# Go-Back-N protocol based on simpy

The Go-Back-N protocol is implemented using a **discrete event system** instead of socket programming. Two schemes, Node0.py and Node1.py, are utilized where Node0.py handles static data while Node1.py manages **dynamic data flow**. These schemes are also capable of handling **multi-node and multi-service scenarios**.


**Packets:**  

​		simpy——4.0.2

**Run the system:** 

​		run main0.py

or	run main1.py

**Reference:**

​		https://github.com/haseeb-saeed/go-back-N