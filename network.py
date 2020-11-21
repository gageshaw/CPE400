import numpy as np
import random as rand
import sys

pFailMax = 1000


class network:
    
    
    
    def __init__(self, numNodes, cycles, sendFreq):
        self.numNodes = numNodes
        self.cycles = cycles
        self.timeCounter = 0
        self.tp = 0 
        self.DistVecCounter = 0
        self.failedNodes = np.empty(0)
        self.sendFreq = sendFreq
        
        print("building nodes")
        #create nodeArr by filling first entry
        pFail = rand.randrange(pFailMax)
        timeCost = rand.randrange(10)
        self.nodeArr = np.array([node(0, pFail, np.array([[1,timeCost], [2,timeCost]]), timeCost,numNodes, self)])
        
        #fill nodeArr -> n=numNodes
        for x in range(1,self.numNodes):
            #create random fail probability and time cost
            pFail = rand.randrange(pFailMax)
            timeCost = rand.randrange(10)
            
            #generate two links != ID
            links = np.array([[self.numNodes,timeCost],[self.numNodes,timeCost]])
            linkGen = rand.randint(0, numNodes-1)
            for y in range(2):
                while(linkGen == x or np.isin(linkGen,links)):
                    linkGen = rand.randint(0,numNodes-1)
                links[y][0] = linkGen
            
            #construct new node and add to nodeArr
            self.nodeArr = np.append(self.nodeArr, node(x, pFail, links, timeCost, numNodes, self))
        
        #initialize bidirectional links
        print("initializing links")
        for x in range(self.numNodes):
            self.nodeArr[x].linkUp()
            
        #initialize routing table
        print("initializing rt")
        self.initRT()
        
        #run simulation
        self.runSim()
        print("Throughput: ", self.tp, "\nDistance Vectors Sent: ",self.DistVecCounter,"\nFailed Nodes:\n",self.failedNodes)
        
    def runSim(self):
        for x in range(self.cycles):
            print("Cycle ",x)
            self.pulse(x)
            
    def initRT(self):
        for x in range(self.numNodes):
            self.nodeArr[x].initRT()
        for x in range(self.numNodes):
            self.nodeArr[x].updateRT()
            
    def pulse(self, counter):
        for x in range(self.numNodes):
            self.nodeArr[x].pulseRecieve(counter)
        
    def printNodes(self):
        for x in range(self.numNodes):
            self.nodeArr[x].pNode()
    
    def incrementTp(self):
        self.tp+=1
    
    def incrementDistVecCounter(self):
        self.DistVecCounter+=1
   
            
#==================        NODE CLASS          ===========================
class node:

    def __init__(self, ID, pFail, links, timeCost, numNodes, nw):
        self.ID = ID
        self.on = True
        self.distVecToSend = False
        self.pFail = pFail
        self.links = links
        self.timeCost = timeCost
        self.rTable = np.full((numNodes,numNodes,2), float('inf'))
        for (i,j,k),val in np.ndenumerate(self.rTable):
            if(i==self.ID and j==self.ID):
                self.rTable[i][j]=[self.ID,0]
        self.queue = np.empty(0)
        self.nw = nw
   
    def pulseRecieve(self,cycles):
        self.recievePac()
        #shut off router
        if(self.pFail == cycles):
            self.on = False
            self.nw.failedNodes = np.append(self.nw.failedNodes, self.ID)
            for i in range(self.nw.numNodes):
                self.rTable[self.ID][i] = np.array([float('inf'),float('inf')])
            self.sendDistVec()
        if(self.on):
            #generate new packet every sendFreq cycles
            if(cycles%self.nw.sendFreq==0):
                newPac = rand.randrange(self.nw.numNodes)
                while(newPac == self.ID):
                    newPac = rand.randrange(self.nw.numNodes)
                self.queue = np.append(self.queue, newPac)
                
            if(self.distVecToSend):
                self.sendDistVec()
            elif(self.queue.size > 0):
                self.sendPac()
            
        
            
            
    #===========================  Revise infinity exception for this func =======================================
    def sendPac(self):
        dest = int(self.queue[0])
        self.queue = np.delete(self.queue, [0])
        #find next hop for packet
        nextHop = int(self.rTable[self.ID][dest][0])
        if(nextHop != float('inf')):
            #place packet in nextHop's queue
            self.nw.nodeArr[nextHop].queue = np.append(self.nw.nodeArr[nextHop].queue,dest)

    def recievePac(self):
        recievedPackets = np.where(self.queue == self.ID)
        recievedPackets = recievedPackets[0].astype(int)
        self.queue = np.delete(self.queue, recievedPackets)
        for i,val in enumerate(recievedPackets):
            self.nw.incrementTp()


    #establish bidirectional links with neighbors (used upon network creation)
    def linkUp(self):
        #append nodes ID to neighbors link arrays
        for x in range(2):
            neighborLinks = self.nw.nodeArr[self.links[x][0]].links 
           
            timeCostN = self.nw.nodeArr[self.links[x][0]].timeCost
            #check if link is already included 
            if(not np.isin(self.ID,neighborLinks[:,0])):
                if(timeCostN > self.timeCost):
                    self.nw.nodeArr[self.links[x][0]].links  = np.append(neighborLinks, [[self.ID,timeCostN]],axis=0)
                    self.links[x][1] = timeCostN
                else:
                    self.nw.nodeArr[self.links[x][0]].links  = np.append(neighborLinks, [[self.ID,self.timeCost]],axis=0)
                                    
            else:
                if(timeCostN > self.timeCost):
                    self.links[x][1] = timeCostN
                else:
                    linkLoc = np.where(neighborLinks[:,0]==self.ID)
                    linkLoc = linkLoc[0][0]
                    self.nw.nodeArr[self.links[x][0]].links[linkLoc][1] = self.timeCost
     
    #update routing tables with bellman/ford eqn
    def updateRT(self):
        update = False
        
        #compare nTable with rTable and update rTable
        for i,val1 in enumerate(self.rTable[self.ID]):
            costArr = np.zeros((self.nw.numNodes,2))
            for j,val2 in enumerate((self.rTable[:,i])):
                costArr[j][1] = self.rTable[self.ID][j][1] + val2[1]
                costArr[j][0] = j
            minCost = min(costArr[:,1])
            if(minCost<val1[1]):
                update = True
                minIndex = np.where(costArr[:,1]==minCost)[0][0]
                self.rTable[self.ID][i] = costArr[minIndex]
        if(update):
            distVecToSend = True
            
    def updateRTinit(self):
        update = False
        
        #compare nTable with rTable and update rTable
        for i,val1 in enumerate(self.rTable[self.ID]):
            costArr = np.zeros((self.nw.numNodes,2))
            for j,val2 in enumerate((self.rTable[:,i])):
                costArr[j][1] = self.rTable[self.ID][j][1] + val2[1]
                costArr[j][0] = j
            minCost = min(costArr[:,1])
            if(minCost<val1[1]):
                update = True
                minIndex = np.where(costArr[:,1]==minCost)[0][0]
                self.rTable[self.ID][i] = costArr[minIndex]
        if(update):
            self.sendDistVecInit()
    
    #fill my row in routing table with direct link costs
    def initRT(self):
        for i,val in enumerate(self.links):
            self.rTable[self.ID][val[0]] = val
        self.sendDistVecInit()
            
        
            
    #send dist vec to neighbors routing table
    def sendDistVec(self):
        for i,val in enumerate(self.links):
            self.nw.nodeArr[val[0]].rTable[self.ID]= self.rTable[self.ID]
            self.nw.incrementDistVecCounter()
            self.nw.nodeArr[val[0]].updateRT()
            
    def sendDistVecInit(self):
        for i,val in enumerate(self.links):
            self.nw.nodeArr[val[0]].rTable[self.ID]= self.rTable[self.ID]
            self.nw.nodeArr[val[0]].updateRTinit()
        
    #print node info
    def pNode(self):
        print("I'm node: ", self.ID)
        print("pFail: ", self.pFail)
        print("links: ", self.links)
        print("timeCost: ", self.timeCost)
        print("rTable:\n", self.rTable)
        #print("queue: ", self.queue)
   

