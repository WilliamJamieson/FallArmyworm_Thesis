import bokeh.plotting as plt
import bokeh.layouts      as lay

import multi_gen.period as period
import multi_gen.runs   as runs

save_file = 'susceptible_sim_0_bt_period_plots.html'
plt.output_file(save_file)


sim = period.PlotData.create(runs.runs[1])

layout = lay.column(
    sim[runs.summaries[0]][runs.tables[1]][runs.columns[2]][runs.reg],
    sim[runs.summaries[0]][runs.tables[1]][runs.columns[2]][runs.log],
    sim[runs.summaries[1]][runs.tables[1]][runs.columns[2]][runs.reg],
    sim[runs.summaries[1]][runs.tables[1]][runs.columns[2]][runs.log],
    sim[runs.summaries[0]][runs.tables[2]][runs.columns[2]][runs.reg],
    sim[runs.summaries[0]][runs.tables[2]][runs.columns[2]][runs.log],
    sim[runs.summaries[1]][runs.tables[2]][runs.columns[2]][runs.reg],
    sim[runs.summaries[1]][runs.tables[2]][runs.columns[2]][runs.log],
)
plt.show(layout)
