import network as n
import importlib
importlib.reload(n)

numSims = 100
pFailMax = 201
cycles = 200


n.runSim(numSims, 5, cycles, pFailMax, 4)
