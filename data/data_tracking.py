import source.keyword as keyword


genotype_attr = (keyword.genotype_keys, False)
genotype      = {keyword.genotype: genotype_attr}

genotype_attrs = {keyword.egg:    genotype,
                  keyword.larva:  genotype,
                  keyword.pupa:   genotype,
                  keyword.female: genotype}

death_attr = (keyword.death_keys, True)
death      = {keyword.death: death_attr}

genotype_death = {**genotype, **death}

genotype_death_attrs = {agent_key: genotype_death
                            for agent_key in keyword.insect_keys}
