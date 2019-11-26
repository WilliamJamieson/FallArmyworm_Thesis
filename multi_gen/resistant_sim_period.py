import bokeh.plotting as plt
import bokeh.layouts      as lay

import multi_gen.period as period
import multi_gen.runs   as runs

save_file = 'resistant_sim_period_plots.html'
plt.output_file(save_file)


resistant_sim = period.PlotData.create(runs.runs[0])

layout = lay.column(
    resistant_sim[runs.summaries[0]][runs.tables[1]][runs.columns[0]][runs.reg],
    resistant_sim[runs.summaries[0]][runs.tables[1]][runs.columns[0]][runs.log],
    resistant_sim[runs.summaries[1]][runs.tables[1]][runs.columns[0]][runs.reg],
    resistant_sim[runs.summaries[1]][runs.tables[1]][runs.columns[0]][runs.log],
    resistant_sim[runs.summaries[0]][runs.tables[2]][runs.columns[0]][runs.reg],
    resistant_sim[runs.summaries[0]][runs.tables[2]][runs.columns[0]][runs.log],
    resistant_sim[runs.summaries[1]][runs.tables[2]][runs.columns[0]][runs.reg],
    resistant_sim[runs.summaries[1]][runs.tables[2]][runs.columns[0]][runs.log],
)
plt.show(layout)
