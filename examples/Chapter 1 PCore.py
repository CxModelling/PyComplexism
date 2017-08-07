from epidag import DirectedAcyclicGraph

__author__ = 'TimeWz667'


# Read a parameter core from script
script = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lognorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

pc = DirectedAcyclicGraph(script).get_simulation_model()
print('Blueprint of the parameter core')
print(pc)


# Implement a parameter core
pc1 = pc.sample_core()
print('PC based on the blueprint')
print(pc1)

tr = pc1['TrAB']
print('Get distribution of TrAB from the PC')
print(tr)

print('Sample a value from TrAB')
print(tr.sample())
