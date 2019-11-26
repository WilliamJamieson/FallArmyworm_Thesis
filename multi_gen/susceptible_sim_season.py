import bokeh.plotting as plt
import bokeh.palettes as palettes

import multi_gen.season as season
import multi_gen.runs   as runs

colors    = palettes.Colorblind[8]
save_file = 'susceptible_sim_seasonal_plots.html'
plt.output_file(save_file)

plot_width  = 2000
plot_height = 500

line_width       = 3.5
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'


resistant_sim              = season.Seasonal.create(runs.runs[0], 82)
susceptible_sim_0_bt       = season.Seasonal.create(runs.runs[1], 63)
susceptible_sim_70_bt_high = season.Seasonal.create(runs.runs[2], 63)
susceptible_sim_70_bt_low  = season.Seasonal.create(runs.runs[3], 63)
susceptible_sim_90_bt_high = season.Seasonal.create(runs.runs[4], 70)
susceptible_sim_90_bt_low  = season.Seasonal.create(runs.runs[5], 56)

resist      = resistant_sim[             runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[0]].iloc[1000:]
sus_0       = susceptible_sim_0_bt[      runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
sus_70_high = susceptible_sim_70_bt_high[runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
sus_70_low  = susceptible_sim_70_bt_low[ runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
sus_90_high = susceptible_sim_90_bt_high[runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
sus_90_low  = susceptible_sim_90_bt_low[ runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]

reg_plot = plt.figure(plot_height=plot_height,
                      plot_width=plot_width)
reg_plot.title.text = 'Time-Series'
reg_plot.xaxis.axis_label = 'time (days)'
reg_plot.yaxis.axis_label = 'population'

reg_plot.line(resist.index, resist,
              line_width=line_width,
              color=colors[0],
              legend='Resistant Population')
reg_plot.line(sus_0.index, sus_0,
              line_width=line_width,
              color=colors[1],
              legend='Susceptible 0% Bt Population')
reg_plot.line(sus_70_low.index, sus_70_low,
              line_width=line_width,
              color=colors[2],
              legend='Susceptible Low Survival 70% Bt Population')
reg_plot.line(sus_70_high.index, sus_70_high,
              line_width=line_width,
              color=colors[2],
              line_dash='dashed',
              legend='Susceptible High Survival 70% Bt Population')
reg_plot.line(sus_90_low.index, sus_90_low,
              line_width=line_width,
              color=colors[3],
              legend='Susceptible Low Survival 90% Bt Population')
reg_plot.line(sus_90_high.index, sus_90_high,
              line_width=line_width,
              color=colors[3],
              line_dash='dashed',
              legend='Susceptible High Survival 90% Bt Population')
# reg_plot.line(list(larva.keys()), list(larva.values()),
#               line_width=line_width,
#               color=colors[1],
#               legend='Larva')
# reg_plot.line(list(pupa.keys()), list(pupa.values()),
#               line_width=line_width,
#               color=colors[2],
#               legend='Pupa')
# reg_plot.line(list(female.keys()), list(female.values()),
#               line_width=line_width,
#               color=colors[3],
#               legend='Adult')

reg_plot.legend.location = "bottom_right"

reg_plot.legend.label_text_font_size = legend_font_size
reg_plot.title.text_font_size = title_font_size
reg_plot.yaxis.axis_line_width = axis_line_width
reg_plot.xaxis.axis_line_width = axis_line_width
reg_plot.yaxis.axis_label_text_font_size = axis_font_size
reg_plot.xaxis.axis_label_text_font_size = axis_font_size
reg_plot.yaxis.major_label_text_font_size = axis_tick_font_size
reg_plot.xaxis.major_label_text_font_size = axis_tick_font_size
reg_plot.ygrid.grid_line_width = grid_line_width
reg_plot.xgrid.grid_line_width = grid_line_width

plt.show(reg_plot)
#
# # layout = lay.column(
# #     resistant_sim['mean']['(0,)_larva'][runs.observed],
# #     resistant_sim['mean']['(0,)_larva'][runs.trend],
# #     resistant_sim['mean']['(0,)_larva'][runs.season],
# #     resistant_sim['mean']['(0,)_larva'][runs.resid],
# # )
# # plt.show(layout)
