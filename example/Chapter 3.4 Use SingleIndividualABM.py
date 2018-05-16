import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag

__author__ = 'TimeWz667'

dbp = cx.read_dc(cx.load_txt('scripts/SIR_BN.txt'))
pc = dag.quick_build_parameter_core(cx.load_txt('scripts/pSIR.txt'))
dc = dbp.generate_model('M1', **pc.get_samplers())

ag = ss.StSpAgent('Helen', dc['Sus'], pc)

model = cx.SingleIndividualABM('M1', ag)

print(cx.simulate(model, None, 0, 10, 1))
