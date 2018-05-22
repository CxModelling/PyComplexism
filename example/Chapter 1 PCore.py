import epidag as dag
import complexism as cx

__author__ = 'TimeWz667'


# Read a parameter core from script
script = """
PCore ABC{
    beta ~ exp(0.5)
    TrAB ~ lnorm(beta, 1)
    TrBC ~ gamma(beta, 100)
    TrCA ~ k(100)
}
"""

bn = dag.bn_from_script(script)
print('Blueprint of the parameter core')
print(bn)


# Implement a parameter core
res = dag.sample(bn)
print('PC based on the blueprint')

for k, v in res.items():
    print(k, ': ', v)

print()

sc = dag.as_simulation_core(bn)

pc = sc.generate('pc')

print('Sample a value from TrAB')
tr = pc.get_sampler('TrAB')
print(tr())
