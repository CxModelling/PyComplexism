from dzdy import *
import matplotlib.pyplot as plt


par_script = """ 
PCore pSIR{
    transmission_rate = 0.5
    rec_rate ~ triangle(0.05, 0.1, 0.15)
    beta ~ exp(transmission_rate)
    gamma ~ exp(rec_rate)
    Die ~ exp(0.02)
}
"""

dc_ctbn_script = """
CTBN SIR_BN{
    life[Alive | Dead]
    sir[S | I | R]

    Alive{life:Alive}
    Dead{life:Dead}
    Inf{life:Alive, sir:I}
    Rec{life:Alive, sir:R}
    Sus{life:Alive, sir:S}

    Die -> Dead # from transition Die to state Dead by distribution Die
    Sus -- Infect(beta) -> Inf 
    Inf -- Recov(gamma) -> Rec

    Alive -- Die # from state Alive to transition Die
}
"""

da = Director()
da.read_pc(par_script)
da.read_dc(dc_ctbn_script)
cfd = da.new_mc('ABM_SIR', 'ABM', tar_pc='pSIR', tar_dc='SIR_BN')
cfd.add_trait(trt_type='Distribution', trt_name='BMI', Distribution='norm(23,5)')

cfd.add_network('IDU', 'BA', m=2)
cfd.add_behaviour('cycle', be_type='Reincarnation', s_birth='Sus', s_death='Dead')
cfd.add_behaviour('transmission', be_type='NetShock', s_src='Inf', t_tar='Infect', net='IDU')

cfd.set_observations(states=['Sus', 'Inf', 'Rec'], behaviours=['transmission'])

mod_src, out_src = da.simulate('ABM_SIR', y0={'Sus': 45, 'Inf': 5}, fr=0, to=10)
out_src.plot()
plt.show()

mod_new = da.copy_model(mod_src)
out_src = update(mod_src, 20)
out_src.plot()
out_new = update(mod_new, 20)
out_new.plot()
plt.show()