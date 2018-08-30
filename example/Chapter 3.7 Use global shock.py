import matplotlib.pyplot as plt
import complexism as cx


ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pSIR.txt')
ctrl.load_state_space_model('scripts/SIR_BN.txt')


abm = ctrl.new_sim_model('SIR', 'StSpABM')
abm.set_agent(dynamics='SIR', prefix='Ag')
abm.add_behaviour('FOI', 'FDShock', s_src='Inf', t_tar='Infect')
abm.add_behaviour('Life', 'Reincarnation', s_birth='Sus', s_death='Dead')
abm.set_observations(states=['Sus', 'Inf', 'Rec', 'Alive'],
                     transitions=['Infect', 'Recov', 'Die'],
                     behaviours=['FOI'])


if __name__ == '__main__':
    model = ctrl.generate_model('M7', 'SIR', bn='pSIR')

    y0 = [
        {'n': 90, 'attributes': {'st': 'Sus'}},
        {'n': 10, 'attributes': {'st': 'Inf'}}
    ]

    cx.start_counting()
    output = cx.simulate(model, y0, 0, 15, .5)
    cx.stop_counting()
    print(cx.get_results())

    output[['Sus', 'Inf', 'Rec', 'Alive', 'FOI']].plot()

    plt.show()
