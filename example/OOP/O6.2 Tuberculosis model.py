import complexism as cx
import epidag as dag
import matplotlib.pyplot as plt
__author__ = 'TimeWz667'


model_name = 'TB_SER'

# Step 1 set a parameter core
psc = """
PCore pTB {
    r_tr = 5
    r_act = 0.073
    r_ract = 0.073
     
    r_rel = 0.0073
    r_rec = 0.2 
    r_death = 0.025
    r_tb_death = 0.2
}
"""

bn = cx.read_bn_script(psc)
sm = dag.as_simulation_core(bn, hie={'city': ['SER', 'I'], 'SER': [], 'I': []})
pc = sm.generate('Taipei')


# Step 2 define equations
def TB_ODE(y, t, p, x):
    sus = y[0]
    flat = y[1]
    slat = y[2]


    n = sum(y)
    inf = s*i*p['beta']/n * x['dis']
    rec = i*p['gamma']
    return [-inf, inf-rec, rec]


eqs = cx.OrdinaryDifferentialEquations(SIR_ODE, ['S', 'I', 'R'], dt=.1, x={'dis': 0.5})


# Step 3 generate a model
model = cx.GenericEquationBasedModel(model_name, pc, eqs, dt=.5)


# Step 4 decide outputs
for st in ['S', 'I', 'R']:
    model.add_observing_stock(st)


# Step 5 simulate
y0 = {
    'S': 999,
    'I': 1,
    'R': 0
}

output = cx.simulate(model, y0, 0, 10, 1)



output.plot()

plt.show()
