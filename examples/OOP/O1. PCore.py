from epidag import DirectedAcyclicGraph

__author__ = 'TimeWz667'


script = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lnorm(1/beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

# Generate a simulation model
print('Read script')
sm = DirectedAcyclicGraph(script).get_simulation_model()
print(sm)
print()

# Instantiate a parameter core
print('Fix upstream parameters')
pc = sm.sample_core()
print(pc)
print()
# Extract a leaf distribution
print('Draw five random values from "TrAB"')
trAB = pc['TrAB']
print(trAB.sample(5))