import complexism as cx

director = cx.Director()

director.load_bn('scripts/pSIR.txt')
director.load_dbp('scripts/SIR_BN.txt')


mbp = director.new_mbp('ABM_SIR', 'SSABM')
mbp.set_agent(prefix='Ag', group='agent', dynamics='SIR')
mbp.add_behaviour('FOI', 'FDShockFast', s_src='Inf', t_tar='Infect', dt=0.5)
mbp.set_observations(states=['Sus', 'Inf', 'Rec', 'Alive', 'Dead'],
                     transitions=['Infect', 'Recov', 'Die'],
                     behaviours=['FOI'])


model = director.generate_model('ABM_SIR', 'M1', bn='pSIR', dc='SIR')


y0 = [
    {'n': 290, 'attributes': {'st': 'Sus'}},
    {'n': 10, 'attributes': {'st': 'Inf'}},
]

cx.start_counting()
print(cx.simulate(model, y0, 0, 10, 1))
cx.stop_counting()
print(cx.get_results())
