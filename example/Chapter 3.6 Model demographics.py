import matplotlib.pyplot as plt
import complexism as cx

ctrl = cx.Director()
ctrl.load_bayes_net('scripts/pBAD.txt')
ctrl.load_state_space_model('scripts/BAD.txt')


abm = ctrl.new_sim_model('BAD', 'StSpABM')
abm.set_agent(dynamics='BAD', prefix='Ag')
abm.add_behaviour('Life', 'Reincarnation', s_birth='Young', s_death='Dead')
abm.set_observations(states=['Young', 'Middle', 'Old', 'Alive'], transitions=['Die'])


if __name__ == '__main__':
    model = ctrl.generate_model('M6', 'BAD', bn='pBAD')

    y0 = [
        {'n': 100, 'attributes': {'st': 'Young'}},
        {'n': 100, 'attributes': {'st': 'Middle'}},
        {'n': 100, 'attributes': {'st': 'Old'}}
    ]

    cx.start_counting()
    output = cx.simulate(model, y0, 0, 10, .5)
    cx.stop_counting()
    print(cx.get_results())

    output.plot()
    plt.show()
