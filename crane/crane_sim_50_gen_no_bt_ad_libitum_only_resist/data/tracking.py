import source.keyword as keyword


genotype_attr = (keyword.genotype,
                 keyword.genotype_keys,
                 False)
genotype      = {keyword.genotype: genotype_attr}

genotype_attrs = {agent_key: genotype
                    for agent_key in keyword.insect_keys}

death_attr = (keyword.death,
              keyword.death_keys,
              True)
death      = {keyword.death: death_attr}

death_attrs = {agent_key: death
                  for agent_key in keyword.insect_keys}

death_filter_attr = (keyword.death,
                     keyword.death_keys,
                     {keyword.genotype:
                          (keyword.genotype_keys,
                           True)
                      })
death_filter = {keyword.death_track: death_filter_attr}

death_filter_attrs = {agent_key: death_filter
                        for agent_key in keyword.insect_keys}

genotype_death       = {**genotype, **death}
genotype_death_attrs = {agent_key: genotype_death
                            for agent_key in keyword.insect_keys}

genotype_death_filters = {**genotype, **death_filter}
genotype_death_filters_attrs = {agent_key: genotype_death_filters
                                    for agent_key in keyword.insect_keys}
