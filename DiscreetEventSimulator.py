# All Rights Reserved
# 
# Copyright (c) 2020 Yisroel Mirsky
# 
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numpy as np
import networkx as nx
from queue import PriorityQueue
import time


class Agent:
    def __init__(self,my_ID,L):
        global G # use the network declared globally
        self.pb = {}
        self.last_absorb_epoch = 0
        self.cur_epoch = 0
        self.L = L # number of records in a block
        self.chain = [] #in this sim, the ids are used inplace of the full record
        self.my_ID = my_ID # node index (ID) of this agent in G

    # add self to pb if it's not there, and close block if it's complete
    def check_self_status(self):
        if (len(self.pb) < self.L) and (self.pb.get(self.my_ID) is None):  # if own model is not in PB and not at block limit
            self.pb[self.my_ID] = True  # add self
        if len(self.pb) == self.L: #close block
            #close the block
            self.chain.append(self.pb)
            self.pb = {self.my_ID : True}
            # for simulator stats:
            global completed_block_count
            if completed_block_count < len(self.chain): #only update stats if i'm first
                global completed_block_agent
                global completed_block_epochs
                completed_block_count += 1
                completed_block_agent = self.my_ID
                completed_block_epochs = self.cur_epoch
            self.cur_epoch = 0


    # send my current chain+pb to all neighbors
    def broadcast(self):
        for nnode in G[self.my_ID]:
            G.node[nnode]['agent'].receive_chain(self.chain,self.pb)
        self.cur_epoch+=1

    # a neighbor suggested a chain+pb to me, I'll swap mine out if it is longer
    def receive_chain(self, other_chain, other_pb):
        self.process_received_chain(other_chain, other_pb)
        #if no update after 15 epochs, assume deadlock and direct message 3 of the missing IDs
        if (self.cur_epoch - self.last_absorb_epoch) > 15:
            self.send_direct_chain(reference_pb=other_pb)

    # Somebody in the network suggested a pb to me, I'll swap mine out (absorb) if it is longer
    def receive_direct_chain(self, other_chain, other_pb):
        self.process_received_chain(other_chain, other_pb)

    #direct message 3 of the missing IDs in other_pb with my chain
    def send_direct_chain(self,reference_pb):
        if self.pb == reference_pb:
            return
        self.last_absorb_epoch = self.cur_epoch #sleep a bit - don't do this every epoch
        missing_ids = np.setdiff1d(np.array(list(reference_pb.keys()),dtype=int),np.array(list(self.pb.keys()),dtype=int),assume_unique=True)
        if len(missing_ids)>0:
            sample = np.random.choice(missing_ids, np.min((3, len(missing_ids))),replace=False)
            for id in sample:  # send 'broadcast' to missing nodes (direct messages) suggesting my pb
                G.nodes[id]['agent'].receive_direct_chain(self.chain,self.pb)
                global dir_message_count
                dir_message_count += 1

    def process_received_chain(self,other_chain, other_pb):
        # Check chain
        if len(other_chain) < len(self.chain):
            return
        if len(other_chain) > len(self.chain):
            # Here one should perform chain validity checks
            self.chain = other_chain.copy()
            self.pb = other_pb.copy()
            return
        if self.is_longer_pb(other_pb):
            # Here, one should perform pb validity and combined model checks
            self.pb = other_pb.copy()
            self.last_absorb_epoch = self.cur_epoch

    def is_longer_pb(self,other_pb):
        # Get len of my pb
        if self.pb.get(self.my_ID) is None:  # I'm not in my pb
            self_pb_len = len(self.pb)
        else:  # I have a record in my pb already
            self_pb_len = len(self.pb) - 1
        # Get len of other pb
        if other_pb.get(self.my_ID) is None:  # I'm not in the other pb
            other_pb_len = len(other_pb)
        else:  # I have a record in the other pb already
            other_pb_len = len(other_pb) - 1
        # Absorb if bigger
        return other_pb_len > self_pb_len




intervals = (
    ('millennia', 31536000000),  # 60*60*24*365*100
    ('centuries', 3153600000),   # 60*60*24*365*10
    ('years', 31536000), # 60*60*24*365
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
    )

def display_time(seconds, granularity=3):
    if seconds < 1:
        return "< 1 second"
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                if name == "centuries":
                    name = "century"
                elif name == "millennia":
                    name = "millennium"
                else:
                    name = name.rstrip('s')
            result.append("{} {}".format(int(value), name))
    return ', '.join(result[:granularity])




class DES:
    # n: number of agents
    # m: graph gen parameter
    # broadcast_interval: agent broadcast interval in seconds (simulated)
    # L: block length
    # graph_type : the type of network generated
    #               smallworld (newman_watts_strogatz): m=the number of neigbors
    #               barabasi (long tail degree distribution): m=prefferantial attachment
    #               complete (all agents are connected to each other): m=None
    def __init__(self,n,m=None,broadcast_interval=1,L=None,graph_type="smallworld"):
        self.n=n
        self.m=m
        self.broadcast_interval=broadcast_interval
        self.L = L
        if self.L is None:
            self.L = n
        elif self.L > n:
            self.L = n
        self.epoch_limit = n * 2  # epoch limit
        global dir_message_count
        global G
        global completed_block_count
        global completed_block_agent
        global completed_block_epochs
        completed_block_epochs = 0
        completed_block_agent = None
        completed_block_count = 0
        dir_message_count = 0
        self.graph_type = graph_type

        self.G = self.buildGraph(n, m, graph_type)
        self.Q = PriorityQueue()
        #init DES Queue
        for id in range(n): #all agents will start broadcasting within the first broadcast_interval
            self.Q.put((np.random.rand()*self.broadcast_interval,id))

    def buildGraph(self,n,m,type):
        global G
        if type == "barabasi":
            G = nx.barabasi_albert_graph(n, m, seed=None)
        elif type == "smallworld":
            G = nx.newman_watts_strogatz_graph(n,m,0.1)
        elif type == "complete":
            G = nx.complete_graph(n)
        else:
            raise("Bad graph type")
        for i in range(n):
            G.nodes[i]['agent'] = Agent(i,self.L)
        return G

    def run(self,num_blocks=1,print_progress=True):
        last_block_count = 0
        last_block_time = 0
        dir_message_total = 0
        epochs_total = 0
        total_exp = 0
        cur_time = 0
        start = time.time()

        print("Running DES to simulate",self.n, "agents over",num_blocks,"blocks:")
        print("L:",self.L)
        print("T:",self.broadcast_interval,"seconds")
        print("Agent Connectivity:",self.graph_type)

        while completed_block_count < num_blocks:
            if self.Q.empty():
                break
            cur_time, agent_id = self.Q.get()
            agent = G.nodes[agent_id]['agent']
            agent.check_self_status() #add self, close pb as next block if ready
            agent.broadcast() #send chain+pb to all neighbors
            self.Q.put((cur_time + self.broadcast_interval + np.random.rand()*.1, agent_id)) #next broadcast is in broadcast_interval + noise

            #collect stats on closed block
            if last_block_count < completed_block_count:
                last_block_count = completed_block_count
                dir_message_total+=dir_message_count
                epochs_total+=int((cur_time-last_block_time)//self.broadcast_interval)
                total_exp += (cur_time-last_block_time)*self.L
                if print_progress:
                    print("(t:"+display_time(cur_time)+") Block #" + str(completed_block_count) + " has been closed by agent " + str(completed_block_agent))
                    print("      It took",display_time(cur_time-last_block_time),"and",int(np.ceil((cur_time-last_block_time)/self.broadcast_interval)),"epochs to close the block.")
                    print("      The current Global Model has",display_time(total_exp),"experience.")
                    print("      There were",dir_message_count,"direct messages sent over the network")
                last_block_time = cur_time
        stop = time.time()

        print("")
        print("===================================")
        print("Simulation Complete:   ("+display_time(stop-start)+")")
        print("===================================")
        print("Simulated time: ",display_time(cur_time))
        print("Completed blocks: ", completed_block_count)
        print("Avrg. time per block: ",display_time(cur_time/completed_block_count))
        print("Avrg. number of epochs per block: ", np.round(epochs_total/completed_block_count,2))
        print("Years experience in current Global Model: ", display_time(total_exp))
        print("Avrg. number of direct messages sent per block: ", np.round(dir_message_total/completed_block_count,2))

        # The network, num_completed_blocks, avrg_epochs_per_block
        return G, completed_block_count, np.round(epochs_total/completed_block_count,2)

