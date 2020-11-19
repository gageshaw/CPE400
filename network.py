import numpy as np
import random as rand

class network:
    
    
    
    def __init__(self, numNodes, cycles):
        self.numNodes = numNodes
        self.cycles = cycles
        self.tp = 0 
        
        #create nodeArr by filling first entry
        pFail = rand.randrange(100)
        timeCost = rand.randrange(100)
        self.nodeArr = np.array([node(0, pFail, np.array([1,2]), timeCost,numNodes, self)])
        
        #fill nodeArr -> n=numNodes
        for x in range(1,self.numNodes):
            #create random fail probability and time cost
            pFail = rand.randrange(100)
            timeCost = rand.randrange(100)
            
            #generate two links != ID
            links = np.array([self.numNodes,self.numNodes])
            linkGen = rand.randint(0, numNodes-1)
            for y in range(2):
                #print("Test ->links, linkGen, x", links, linkGen, x)
                while(linkGen == x or np.isin(linkGen,links)):
                    linkGen = rand.randint(0,numNodes-1)
                #print("Assign ->links, linkGen, x", links, linkGen, x)
                links[y] = linkGen
            
            #construct new node and add to nodeArr
            self.nodeArr = np.append(self.nodeArr, node(x, pFail, links, timeCost, numNodes, self))
            
        for x in range(self.numNodes):
            self.nodeArr[x].linkUp()
            
        #check links (TEMP)
        for x in range(self.numNodes):
            self.nodeArr[x].pNode()
    
    def incrememetTp(self):
        self.tp+=1
        
   
            
#==================        NODE CLASS          ===========================
class node:

    def __init__(self, ID, pFail, links, timeCost, numNodes, nw):
        self.ID = ID
        self.pFail = pFail
        self.links = links
        self.timeCost = timeCost
        self.rTable = np.zeros(((numNodes,numNodes)))
        self.queue = np.zeros(100)
        self.nw = nw
 
    def linkUp(self):
        #append nodes ID to neightbors link arrays
        for x in range(2):
            neighborLinks = self.nw.nodeArr[self.links[x]].links 
            
            if(not np.isin(self.ID,neighborLinks)):
                self.nw.nodeArr[self.links[x]].links  = np.append(neighborLinks, self.ID)
            

    def pNode(self):
        print("I'm node: ", self.ID)
        print("pFail: ", self.pFail)
        print("links: ", self.links)
        print("timeCost: ", self.timeCost)
        print("rTable: ", self.rTable)
        print("queue: ", self.queue)
   
        

