import matplotlib.pyplot as plt
import complexism as cx


ctrl = cx.Director()
ctrl.load_bates_net('scripts/pDzAB.txt')
ctrl.load_state_space_model('scripts/DzAB.txt')


abm = ctrl.new_sim_model('AB', 'StSpABM')
abm.set_agent(dynamics='DzAB', prefix='Ag')
abm.set_observations(states=['ab', 'aB', 'Ab', 'AB'])


if __name__ == '__main__':
    model = ctrl.generate_model('M5', 'AB', bn='pDzAB')

    y0 = [
        {'n': 1000, 'attributes': {'st': 'ab'}}
    ]

    cx.start_counting()
    output = cx.simulate(model, y0, 0, 10, .5)
    cx.stop_counting()
    print(cx.get_results())

    output.plot()
    plt.show()
