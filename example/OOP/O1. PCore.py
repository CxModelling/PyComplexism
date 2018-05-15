import epidag as dag

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
pc = dag.quick_build_parameter_core(script, )
print(pc)

# Extract a leaf distribution
print('Draw five random values from "TrAB"')
trAB = pc.get_sampler('TrAB')
print(trAB.sample(5))
