import numpy as np
import random as rand
import sys




def runSim(iterations, numNodes, cycles, pFailMax, sendFreq, printDistVec=False):
    timeArr = np.zeros(iterations)
    lossArr = np.zeros(iterations)
    dvCountArr_loss = np.zeros(iterations)
    dvCountArr_time = np.zeros(iterations)

    for x in range(iterations):
        n = network(numNodes, cycles, pFailMax, sendFreq, printDistVec)
        timeArr[x] = n.runPartialSim()
        dvCountArr_time[x] = n.DistVecCounter

    for x in range(iterations):

        n = network(numNodes, cycles, pFailMax,
                    sendFreq, printDistVec, time=False)
        lossArr[x] = n.runPartialSim()
        dvCountArr_loss[x] = n.DistVecCounter

    aveTimeTp = np.mean(timeArr)
    aveLossTp = np.mean(lossArr)
    aveDVcounter_loss = np.mean(dvCountArr_loss)
    aveDVcounter_time = np.mean(dvCountArr_time)
    print("Average DV counter using time as cost: ", aveDVcounter_time)
    print("Average throughput using time as cost: ", aveTimeTp)
    print("Average DV counter using unreliability as cost: ", aveDVcounter_loss)
    print("Average throughput using unreliability as cost: ", aveLossTp)


class network:

    def __init__(self, numNodes, cycles, pFailMax, sendFreq, printDistVec, time=True):
        self.numNodes = numNodes
        self.cycles = cycles
        self.timeCounter = 0
        self.tp = 0
        self.DistVecCounter = 0
        self.failedNodes = np.empty(0)
        self.sendFreq = sendFreq

        # create nodeArr by filling first entry
        pFail = rand.randrange(pFailMax)
        timeCost = rand.randrange(1, 10)

        if(time):
            self.nodeArr = np.array([node(0, pFail, pFailMax, np.array(
                [[1, timeCost], [2, timeCost]]), timeCost, numNodes, printDistVec, self)])
        else:
            self.nodeArr = np.array([node(0, pFail, pFailMax, np.array(
                [[1, timeCost], [2, timeCost]]), timeCost, numNodes, printDistVec, self, time=False)])

        # fill nodeArr -> n=numNodes
        for x in range(1, self.numNodes):
            # create random fail probability and time cost
            pFail = rand.randrange(pFailMax)
            timeCost = rand.randrange(1, 10)

            # generate two links != ID
            links = np.array([[self.numNodes, timeCost],
                              [self.numNodes, timeCost]])
            linkGen = rand.randint(0, numNodes-1)
            for y in range(2):
                while(linkGen == x or np.isin(linkGen, links[:, 0])):
                    linkGen = rand.randint(0, numNodes-1)
                links[y][0] = linkGen

            # construct new node and add to nodeArr
            if(time):
                self.nodeArr = np.append(self.nodeArr, node(
                    x, pFail, pFailMax, links, timeCost, numNodes, printDistVec, self))
            else:
                self.nodeArr = np.append(self.nodeArr, node(
                    x, pFail, pFailMax, links, timeCost, numNodes, printDistVec, self, time=False))

        # initialize bidirectional links
        for x in range(self.numNodes):
            self.nodeArr[x].linkUp()

        # initialize routing table
        self.initRT()

    def printRoutingTables(self):
        for x in range(self.numNodes):
            print("DV: ", x)
            print(self.nodeArr[x].rTable[x])

    def runPartialSim(self):
        for x in range(self.cycles):
            self.pulse(x)
        return self.tp

    def initRT(self):
        for x in range(self.numNodes):
            self.nodeArr[x].initRT()
        for x in range(self.numNodes):
            self.nodeArr[x].updateRTinit()

    def pulse(self, counter):
        for x in range(self.numNodes):
            self.nodeArr[x].pulseRecieve(counter)

    def incrementTp(self):
        self.tp += 1

    def incrementDistVecCounter(self):
        self.DistVecCounter += 1


# ==================        NODE CLASS          ===========================
class node:

    def __init__(self, ID, pFail, pFailMax, links, timeCost, numNodes, printDistVec,  nw, time=True):
        self.ID = ID
        self.on = True
        self.pFailMax = pFailMax
        self.printDistVec = printDistVec
        self.distVecToSend = False
        self.pFail = pFail
        self.links = links
        self.timeCost = timeCost
        self.time = time
        self.rTable = np.full((numNodes, numNodes, 2), float('inf'))
        for (i, j, k), val in np.ndenumerate(self.rTable):
            if(i == self.ID and j == self.ID):
                self.rTable[i][j] = [self.ID, 0]
        self.queue = np.empty(0)
        self.nw = nw

    def pulseRecieve(self, cycles):
        self.recievePac()
        # shut off router
        if(self.pFail == cycles):
            if(self.printDistVec):
                self.nw.printRoutingTables()
            self.on = False
            self.nw.failedNodes = np.append(self.nw.failedNodes, self.ID)
            for i in range(self.nw.numNodes):
                for j, val1 in enumerate(self.nw.nodeArr[i].rTable):
                    for k, val2 in enumerate(val1):
                        if(val2[0] == self.ID or k == self.ID):
                            self.nw.nodeArr[i].rTable[j][k] = np.array(
                                [float('inf'), float('inf')])

                self.nw.nodeArr[i].updateRT()
                self.nw.nodeArr[i].distVecToSend = True

        if(self.on):
            # generate new packet every sendFreq cycles
            if(cycles % self.nw.sendFreq == 0):
                newPac = rand.randrange(self.nw.numNodes)
                while(newPac == self.ID):
                    newPac = rand.randrange(self.nw.numNodes)
                self.queue = np.append(self.queue, newPac)
            if(cycles % self.timeCost == 0):
                if(self.distVecToSend):
                    self.sendDistVec()
                    self.distVecToSend = False
                elif(self.queue.size > 0):
                    self.sendPac()

    def sendPac(self):
        dest = int(self.queue[0])
        self.queue = np.delete(self.queue, [0])
        # find next hop for packet
        if(dest != float('inf')):
            nextHop = self.rTable[self.ID][dest][0]
            if(nextHop != float('inf')):
                nextHop = int(nextHop)
                # place packet in nextHop's queue
                self.nw.nodeArr[nextHop].queue = np.append(
                    self.nw.nodeArr[nextHop].queue, dest)

    def recievePac(self):
        recievedPackets = np.where(self.queue == self.ID)
        recievedPackets = recievedPackets[0].astype(int)
        self.queue = np.delete(self.queue, recievedPackets)
        for i, val in enumerate(recievedPackets):
            self.nw.incrementTp()

    # establish bidirectional links with neighbors (used upon network creation)

    def linkUp(self):
        # append nodes ID to neighbors link arrays
        for x in range(2):
            # print(self.links[x][0])
            neighborLinks = self.nw.nodeArr[self.links[x][0]].links
            if(self.time):
                timeCostN = self.nw.nodeArr[self.links[x][0]].timeCost
                timeCostU = self.timeCost
            else:
                timeCostN = self.pFailMax - \
                    self.nw.nodeArr[self.links[x][0]].pFail
                timeCostU = self.pFailMax - self.pFail

            # check if link is already included
            if(not np.isin(self.ID, neighborLinks[:, 0])):
                if(timeCostN > timeCostU):
                    self.nw.nodeArr[self.links[x][0]].links = np.append(
                        neighborLinks, [[self.ID, timeCostN]], axis=0)
                    self.links[x][1] = timeCostN
                else:
                    self.nw.nodeArr[self.links[x][0]].links = np.append(
                        neighborLinks, [[self.ID, timeCostU]], axis=0)

            else:
                if(timeCostN > timeCostU):
                    self.links[x][1] = timeCostN
                else:
                    linkLoc = np.where(neighborLinks[:, 0] == self.ID)
                    linkLoc = linkLoc[0][0]
                    self.nw.nodeArr[self.links[x][0]
                                    ].links[linkLoc][1] = timeCostU

    # update routing tables with bellman/ford eqn
    def updateRT(self):
        update = False
        # compare nTable with rTable and update rTable
        for i, val1 in enumerate(self.rTable[self.ID]):
            costArr = np.zeros((self.nw.numNodes, 2))
            for j, val2 in enumerate((self.rTable[:, i])):
                costArr[j][1] = self.rTable[self.ID][j][1] + val2[1]
                costArr[j][0] = j
            minCost = min(costArr[:, 1])
            if(minCost < val1[1]):
                update = True
                minIndex = np.where(costArr[:, 1] == minCost)[0][0]
                self.rTable[self.ID][i] = costArr[minIndex]
        if(update):
            self.distVecToSend = True

    def updateRTinit(self):
        update = False

        # compare nTable with rTable and update rTable
        for i, val1 in enumerate(self.rTable[self.ID]):
            costArr = np.zeros((self.nw.numNodes, 2))
            for j, val2 in enumerate((self.rTable[:, i])):
                costArr[j][1] = self.rTable[self.ID][j][1] + val2[1]
                costArr[j][0] = j
            minCost = min(costArr[:, 1])
            if(minCost < val1[1]):
                update = True
                minIndex = np.where(costArr[:, 1] == minCost)[0][0]
                self.rTable[self.ID][i] = costArr[minIndex]
        if(update):
            self.sendDistVecInit()

    # fill my row in routing table with direct link costs
    def initRT(self):
        for i, val in enumerate(self.links):
            self.rTable[self.ID][val[0]] = val
        self.sendDistVecInit()

    # send dist vec to neighbors routing table
    def sendDistVec(self):
        for i, val in enumerate(self.links):
            self.nw.nodeArr[val[0]].rTable[self.ID] = self.rTable[self.ID]
            self.nw.incrementDistVecCounter()
            self.nw.nodeArr[val[0]].updateRT()

    def sendDistVecInit(self):
        for i, val in enumerate(self.links):
            self.nw.nodeArr[val[0]].rTable[self.ID] = self.rTable[self.ID]
            self.nw.nodeArr[val[0]].updateRTinit()
