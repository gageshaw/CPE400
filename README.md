# CPE400
networks class project 


The network:
the network constructor creates a randomly connected network of n(specified as input) nodes.  Each node has number of links=l where (2<=l<=n), a random probability of terminal failure (shutting off and never turning back on), and a random cost for all links connected to the node.  When nodes are creating routing tables they will compare costs with their neighbors, and the highest cost between the two nodes associated with the link will become the cost for using that link from either side.  Before a packet is sent through that link it will be delayed the number of cycles associate with the link traversal. The reason the network is randomized is like this is so we can run many simulations and average the outputs of the simulations(throughput, etc.) to get a better idea of how our routing protocols effect the performance of a generalized network. 
