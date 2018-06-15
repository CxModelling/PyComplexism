import complexism as cx
import complexism.agentbased.statespace as ss
import epidag as dag


dbp = cx.read_dbp_script(cx.load_txt('../scripts/SIR_BN.txt'))
pc = dag.quick_build_parameter_core(cx.load_txt('../scripts/pSIR.txt'))
dc = dbp.generate_model('M1', **pc.get_samplers())

ag = ss.StSpAgent('Helen', dc['Sus'], pc)

model = cx.SingleIndividualABM('M1', ag)
model.add_observing_attribute('State')

print(cx.simulate(model, None, 0, 10, 1))
