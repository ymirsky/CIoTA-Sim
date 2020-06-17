# n: number of agents
# m: graph gen parameter
# broadcast_interval: agent broadcast interval in seconds (simulated) "T"
# L: block length
# graph_type : the type of network generated
#               smallworld (newman_watts_strogatz): m=the number of neigbors
#               barabasi (long tail degree distribution): m=prefferantial attachment
#               complete (all agents are connected to each other): m=None


# Here is an example using the DES: agent-based simulator.
# Use this version if you want to follow the protocol and understand how each agent operates
from DiscreetEventSimulator import DES
simulator = DES(n=1000,m=3,broadcast_interval=60,L=800,graph_type="smallworld")
G, num_blocks, epochs_per_block = simulator.run(num_blocks=10, print_progress=True)
