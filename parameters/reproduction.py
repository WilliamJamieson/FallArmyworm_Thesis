import source.keyword as keyword

import parameters.basic_data as data


# Pass through the sex probability
female_prob = data.female_prob

# Pass through fixed values
values = {keyword.trials:          data.trials,
          keyword.limited:         data.limited,
          keyword.lifetime_male:   data.lifetime_male,
          keyword.lifetime_female: data.lifetime_female}
