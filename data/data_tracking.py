import source.keyword as keyword


genotype_attr = (keyword.genotype_keys, False)
genotype      = {keyword.genotype: genotype_attr}

genotype_attrs = {keyword.egg:    genotype,
                  keyword.larva:  genotype,
                  keyword.pupa:   genotype,
                  keyword.female: genotype}

death_attr = (keyword.death_keys, True)
death      = {keyword.death: death_attr}
