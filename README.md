# CPE400: networks class project 

Compiling Instructions:
Specify the number of iterations, number of nodes, cycles, the pFailMax, and the sendFreq. Also indicate if you would like to see the routing tables.
 -> python3 -c 'import network; network.runSim(iterations, numNodes, cycles, pFailMax, sendFreq, printRoutingTable=False)'

THE NETWORK:

Class network:

Member variables:
int numNodes -> number of nodes in network
int cycles -> total number of pulses defining the lifetime of the simulation
int timeCounter -> iterator used to count the pulses elapsed in the simulation
int tp -> current throughput of simulation
int DistVecCounter -> number of distance vectors sent between nodes
int[] failedNodes -> the ID of each failed node 
int sendFreq -> number of pulses that have to elapse before each node generates a new packet
node[] nodeArr -> an array of all class node objects in network 

Methods:
__init__(self, numNodes, cycles, sendFreq, time=True): network
Class constructor
When time=True the cost of each link = timeCost.  
When time=False cost = probabilityOfNodeFailure.  
This polymorphism is used to implement the two routing protocols outlined below. 
Returns class network object
 
runPartialSim(self): tp
pulses network (cycles) times.
Returns total throughput of simulated network.
 
initRT(self): void
initializes routing tables.

pulse(self, counter): void
iterates through all nodes in the network, pulsing each one in turn and sending it the pulse number. 

incrementTp(self): void
increments throughput of the network by one.  This method is called by nodes upon transmitting packets to the final destination. 

incrementDistVecCounter(self): void
increments the distance vector counter of the network by one.  This method is called by nodes when they send an updated distance vector to their neighbors.




NETWORK DESCRIPTIONS:

the network constructor creates a randomly connected network of n(specified as input) nodes. Each node has a number of links=l where (2<=l<=n), a random probability of terminal failure (shutting off and never turning back on -> pFail), a random timeCost for all links connected to the node, and a unique node ID.  The reason the network is randomized like this is so we can run many simulations and average the outputs of the simulations(throughput, etc.) to get a better idea of how our routing protocols affect the performance of a generalized network. 

Time is simulated by 'pulses'.  Pulse(int cycle) is a function that calls each node in the network to perform an action.  The Pulse() function is called by another function runSim(lifetime) which limits the number of pulses to the specified lifetime of the simulation.  Upon receiving a pulse, a node can send a packet or distance vector if cycle%timeCost==0, completing one transmission. This ensures that before information is sent through a link, it will be delayed by the number of cycles = timeCost associated with the link traversal.  

Upon network construction, all the nodes are constructed and the bidirectional links are initialized.  When nodes are initializing links with their neighbors they will compare timeCosts, and the highest cost between the two nodes associated with the link will become the cost used in the nodes routing tables.  The nodes then have a period of 'free' communication (not penalized by their time costs, and outside the scope of the pulse(cycles) function that controls the amount of time the simulation has to run) to establish their routing tables.  There are typically a lot of packets that have to be sent through the network to initialize the routing tables.  Considering this simulation is meant to study the behavior of the network when a node fails, excluding these packets from the scope of the simulation will give us a more clear picture of the performance of our protocols when this happens, and not when the network is 'booting up'. 

The network has a member variable representing the throughput of the network.  Every time a packet reaches its final destination this variable is incremented by one, so that the final throughput of the network at the end of the simulation represents the number of packets successfully delivered to their final destination. 

There are two routing protocols built into the simulator.  One where the cost of each link = maxTimeCost, and one where cost = probabilityOfNodeFailure. The latter protocol will choose optimal routes that avoid nodes that are bound to fail in the hopes of reducing the overhead associated with updating the routing tables.  The former will choose the fastest path through the network. 

THE NODES:

Class node:

Member variables:
int ID -> number used to identify and communicate with the node
int pFail -> number of cycles before node shuts off
int timeCost -> number of cycles that must elapse between transmissions
int[] queue -> queue of packets to be sent
int[][] links -> 2-d array defining all neighbor nodes and the link cost to each neighbor
int[][][] rTable -> nodes routing table 
bool on -> identifies if the node is on or off(the node has failed)
bool distVecToSend -> alerts node that it's distance vector has been updated and should be transmitted to its neighbors 
bool time -> alerts node which routing protocol to use (cost=timeCost, cost=probOfNodeFailure)
network nw -> class network object that the node belongs to

Methods:
__init__(self, ID, pFail, links, timeCost, numNodes, nw, time=True): node 
node class constructor, sets member variables to passed values.

pulseRevieve(self,cycles): void
function called by network.pulse().  Transmits if allowed, generates new packet if allowed, and turns off router if cycles=pFail.  

sendPac(self): void
Takes first entry in the queue, deletes it from the queue, finds the next hop for the packet, and places the packet in the next-hop-router's queue. 

recievePac(self): void
checks the queue for the packet where finalDestination=nodeID.  if found packet(s) is deleted from queue and calls network.incrementTP()

linkUp(self): void
establishes bidirectional links with neighbors where linkCost=(maximum cost of the two link nodes)

updateRT(self): void
checks for lower cost path to all nodes in network, if found updates distance vector and sets distVecToSend=True

sendDistVec(self): void
sends updated distance vectors to neighbor nodes. This is achieved by accessing the neighbors routing table directly, and replacing the row[nodeID] with an updated distance vector. Then, calls network.incrememntDistVecCounter()

updateRTinit(self): void
same as updateRT() except it sends updated distance vector to neighbors when update is found.  This circumnavigates the pulse functionality of the simulation and allows the routing tables to be initialized before simulation begins. 

sendDistVecInit(self): void
same as sendDistVec() except it does not call network.incrememntDistVecCounter()



NODE DESCRIPTIONS:

The routing tables outlined in the course lecture only had one value per entry: the cost of the lowest-cost-path corresponding to the row and column of the entry.  The routing tables in this implementation have the cost of the lowest-cost-path, as well as the ID for the next hop along that path.  This makes the task of routing packets quite simple for each node, the node simply has to consult its own distance vector at the index of the final destination of the packet to find the next hop for said packet. 

The packets sent between nodes are integer values representing the final destination of the packet.  Each node has an unbounded queue of these integers (implemented as a 1d array).  When a node is allowed to transmit a packet, it checks it's routing table for the next hop on the packets journey to its final destination, deletes the packet from its own queue, and appends the packet (integer) directly into the queue of the next hop node. 

Routing vectors are always given priority over packets when a node is allowed to transmit.  That is, if a node has an updated routing vector that needs to be delivered to its neighbors, it uses its transmission to send the routing vector and ignores it's queue of packets until it no longer has an updated distance vector to send. If there is no routing vector to send, the first packet in the queue is transmitted. 

Every pulse, a node checks it's queue for packets that match its node ID.  That means that the packet has reached its final destination.  When such a packet is found it is removed from the queue, and the throughput of the network is incremented by one. 

New packets are generated by each node every sendFreq time cycle.  The packet is generated by producing a random integer (0<i<numNodes, i!=currentNodeID) and appending that integer to its own queue.  

The timeCost associated with each node is static throughout each simulation.  This means that the routing tables are only updated when a node fails.  


THE SIMULATOR:

function -> runSim(iterations):
runs the specified number of individual simulations with both routing protocols described above.  Averages the throughput of each simulation set and returns both averaged throughput values. 




