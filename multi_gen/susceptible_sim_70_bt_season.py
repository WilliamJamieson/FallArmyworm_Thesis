import bokeh.plotting as plt
import bokeh.layouts      as lay

import multi_gen.season as season
import multi_gen.runs   as runs

save_file = 'susceptible_sim_70_bt_season_plots.html'
plt.output_file(save_file)


resistant_sim = season.PlotLowHighData.create(runs.runs[2],
                                              runs.runs[3],
                                              21, [runs.columns[2]])

layout = lay.column(
    resistant_sim['mean']['(0,)_larva'][runs.observed],
    resistant_sim['mean']['(0,)_larva'][runs.trend],
    resistant_sim['mean']['(0,)_larva'][runs.season],
    resistant_sim['mean']['(0,)_larva'][runs.resid],
)
plt.show(layout)
