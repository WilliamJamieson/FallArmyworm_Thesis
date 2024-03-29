import os
import sys

import parameters.model_parameters as param

import models.development  as develop
import models.forage       as forage
import models.growth       as growth
import models.init_biomass as init_bio
import models.movement     as move
import models.reproduction as repro
import models.simulator    as simulator
import models.survival     as survive



bt_prop   = param.bt_prop_0
dominance = param.dominance_1
cannib    = param.cannib_0
sur       = param.larva_prob_bt_low_ss

nums = (
    (0,                 0, 0),
    (0,                 0, 0),
    (0,                 0, 0),
    (0,                 0, 0),
    (param.mix_preg_rr, 0, param.mix_preg_ss)
)

input_models = [
    growth.max_gut(),
    growth.growth(param.alpha_ss,
                  param.alpha_rr,
                  param.beta_ss,
                  param.beta_rr,
                  dominance),
    init_bio.init_num(param.lam_0_egg),
    init_bio.init_mass(param.mu_0_egg_ss,
                       param.mu_0_egg_rr,
                       param.sig_0_egg_ss,
                       param.sig_0_egg_rr,
                       dominance),
    init_bio.init_juvenile(param.mu_0_larva_ss,
                           param.mu_0_larva_rr,
                           param.sig_0_larva_ss,
                           param.sig_0_larva_rr,
                           dominance),
    init_bio.init_mature(param.mu_0_mature_ss,
                         param.mu_0_mature_rr,
                         param.sig_0_mature_ss,
                         param.sig_0_mature_rr,
                         dominance),
    init_bio.init_plant(param.mu_leaf,
                        param.sig_leaf),
    develop.egg_dev(param.mu_egg_dev,
                    param.sig_egg_dev),
    develop.larva_dev(param.mu_larva_dev_ss,
                      param.mu_larva_dev_rr,
                      param.sig_larva_dev_ss,
                      param.sig_larva_dev_rr,
                      dominance),
    develop.pupa_dev(param.mu_pupa_dev,
                     param.sig_pupa_dev),
    forage.adlibitum(param.forage_steps),
    forage.egg(param.egg_factor),
    forage.larva(param.larva_factor),
    forage.fight(param.fight_slope),
    forage.encounter(cannib),
    forage.radius(param.cannibalism_radius),
    move.larva(param.larva_scale,
               param.larva_shape),
    move.adult(param.adult_scale,
               param.adult_shape),
    repro.mating(param.mate_encounter),
    repro.radius(param.mate_radius),
    repro.fecundity(param.fecundity_maximum,
                    param.fecundity_decay),
    repro.density(param.eta,
                  param.gamma),
    repro.init_sex(param.female_prob),
    survive.egg_sur(param.egg_prob),
    survive.pupa_sur(param.pupa_prob),
    survive.adult_sur(param.adult_prob),
    survive.larva_sur(param.larva_prob_non_bt_rr,
                      param.larva_prob_non_bt_ss,
                      param.larva_prob_bt_rr,
                      sur,
                      dominance)
]

base_dir = sys.argv[0].split('.')[0]
base_save = base_dir.split('/')[-1]

try:
    work_path = os.environ['WORK']
    path_save = '{}/{}/{}'.format(work_path,
                                  'FallArmyworm_Thesis',
                                  base_save)

    if not os.path.isdir(path_save):
        print('Creating save directory')
        os.mkdir(path_save)

except KeyError:
    path_save = os.path.dirname(os.path.abspath(__file__))
    print('Falling back to local save')

print('Save path: {}'.format(path_save))

if __name__ == '__main__':
    if len(sys.argv) > 1:
        run_number = sys.argv[1]
    else:
        run_number = 0

    simulator.Simulator.run(run_number,
                            nums,
                            bt_prop,
                            input_models,
                            path_save,
                            base_save)
