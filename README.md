# A Collaborative Anomaly Detection for IoTs over Blockchain Simulator

## Overview

In this repository you will find a Python-based discreet event simulator (DES) for a blockchain protocol which can be used by IoTs to collaborativly train an anomaly detection model and detect/mitigate malicous models/devices (see our paper for details).
The DES is object oriented and creates an instance of each agent to help users follow the protocol logic and the propagation of the chains. The DES only simulates the high level protocol logic, and not the model-attestation training or combining. For code on model management, please see (our other repository).
The user selects the number of agents, the block size (L), and intel sharing interval (T), the number of blocks to close, and the connectivity between the agents. The connectivity can be set to fully connected or random (preferential attachment or small world). The DES queue then manages the agent's information sharing (when elapses of T) where some small amount of noise is added to the event times.

For more information, and if you use this code, please cite our paper:

*Yisroel Mirsky, Tomber Golomb, and Yuval Elovici. Lightweight Collaborative Anomaly Detection 
for the IoT using Blockchain. Journal of Parallel and Distributed Computing. Elsevier. 2020.*

## Dependencies

The networkx module is required:
```
$> pip install networkx
```

## Using the Code

To run the DES, please see the exmaple.py provided in the repo. The basic usage is as follows:
```
# n: number of agents
# m: graph gen parameter
# broadcast_interval: agent broadcast interval in seconds (simulated) "T"
# L: block length
# graph_type : the type of network generated
#               smallworld (newman_watts_strogatz): m=the number of neigbors
#               barabasi (long tail degree distribution): m=prefferantial attachment
#               complete (all agents are connected to each other): m=None

from DiscreetEventSimulator import DES
simulator = DES(n=1000,m=3,broadcast_interval=60,L=800,graph_type="smallworld")
G, num_blocks, epochs_per_block = simulator.run(num_blocks=5, print_progress=True)
```

Example Output:

```
Running DES to simulate 1000 agents over 10 blocks:
L: 800
T: 60 seconds
Agent Connectivity: smallworld
(t:5 hours, 59 minutes, 23 seconds) Block #1 has been closed by agent 422
      It took 5 hours, 59 minutes, 23 seconds and 360 epochs to close the block.
      The current Global Model has 28 weeks, 3 days, 15 hours experience.
      There were 0 direct messages sent over the network
(t:12 hours, 37 seconds) Block #2 has been closed by agent 696
      It took 6 hours, 1 minute, 14 seconds and 362 epochs to close the block.
      The current Global Model has 1 year, 5 weeks, 8 hours experience.
      There were 0 direct messages sent over the network
...

(t:2 days, 12 hours, 16 minutes) Block #10 has been closed by agent 865
      It took 5 hours, 59 minutes, 17 seconds and 360 epochs to close the block.
      The current Global Model has 5 years, 26 weeks, 1 day experience.
      There were 0 direct messages sent over the network

===================================
Simulation Complete:   (1 minute, 8 seconds)
===================================
Simulated time:  2 days, 12 hours, 16 minutes
Completed blocks:  10
Avrg. time per block:  6 hours, 1 minute, 36 seconds
Avrg. number of epochs per block:  361.2
Years experience in current Global Model:  5 years, 26 weeks, 1 day
Avrg. number of direct messages sent per block:  0.0
License
All rights reserved Yisroel Mirsky 2020. Please see the license file in the repository
```

## Full Citation

```
@article{mirsky2020collab,
title = "Lightweight Collaborative Anomaly Detection for the IoT using Blockchain",
journal = "Journal of Parallel and Distributed Computing",
year = "2020",
author = "Yisroel Mirsky, Tomber Golomb, and Yuval Elovici",
}
```
