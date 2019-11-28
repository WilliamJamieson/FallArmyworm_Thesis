import bokeh.plotting as plt
import bokeh.layouts  as lay
import bokeh.palettes as palettes

import numpy as np

import parameters.model_parameters as param

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

larva_resist      = resistant_sim[             runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[0]].iloc[1000:]
larva_sus_0       = susceptible_sim_0_bt[      runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
larva_sus_70_high = susceptible_sim_70_bt_high[runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
larva_sus_70_low  = susceptible_sim_70_bt_low[ runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
larva_sus_90_high = susceptible_sim_90_bt_high[runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]
larva_sus_90_low  = susceptible_sim_90_bt_low[ runs.summaries[0]][runs.tables[1]][runs.trend][runs.columns[2]].iloc[1000:]

susceptible_sim_0_bt       = season.Seasonal.create(runs.runs[1], 64)
susceptible_sim_90_bt_high = season.Seasonal.create(runs.runs[4], 69)

pupa_resist      = resistant_sim[             runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]].iloc[1000:]
pupa_sus_0       = susceptible_sim_0_bt[      runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]].iloc[1000:]
pupa_sus_70_high = susceptible_sim_70_bt_high[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]].iloc[1000:]
pupa_sus_70_low  = susceptible_sim_70_bt_low[ runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]].iloc[1000:]
pupa_sus_90_high = susceptible_sim_90_bt_high[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]].iloc[1000:]
pupa_sus_90_low  = susceptible_sim_90_bt_low[ runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]].iloc[1000:]

larva_plot = plt.figure(plot_height=plot_height,
                        plot_width=plot_width)
larva_plot.title.text = 'Larva Time-Series'
larva_plot.xaxis.axis_label = 'time (days)'
larva_plot.yaxis.axis_label = 'population'

larva_plot.line(larva_resist.index, larva_resist,
                line_width=line_width,
                color=colors[0],
                legend='Resistant Population')
larva_plot.line(larva_sus_0.index, larva_sus_0,
                line_width=line_width,
                color=colors[1],
                legend='Susceptible 0% Bt Population')
larva_plot.line(larva_sus_70_low.index, larva_sus_70_low,
                line_width=line_width,
                color=colors[2],
                legend='Susceptible {} Survival 70% Bt Population'.format(np.round(param.larva_prob_bt_low_ss, 3)))
larva_plot.line(larva_sus_70_high.index, larva_sus_70_high,
                line_width=line_width,
                color=colors[2],
                line_dash='dashed',
                legend='Susceptible {} Survival 70% Bt Population'.format(np.round(param.larva_prob_bt_high_ss, 3)))
larva_plot.line(larva_sus_90_low.index, larva_sus_90_low,
                line_width=line_width,
                color=colors[3],
                legend='Susceptible {} Survival 90% Bt Population'.format(np.round(param.larva_prob_bt_low_ss, 3)))
larva_plot.line(larva_sus_90_high.index, larva_sus_90_high,
                line_width=line_width,
                color=colors[3],
                line_dash='dashed',
                legend='Susceptible {} Survival 90% Bt Population'.format(np.round(param.larva_prob_bt_high_ss, 3)))

larva_plot.legend.location = "bottom_right"

larva_plot.legend.label_text_font_size = legend_font_size
larva_plot.title.text_font_size = title_font_size
larva_plot.yaxis.axis_line_width = axis_line_width
larva_plot.xaxis.axis_line_width = axis_line_width
larva_plot.yaxis.axis_label_text_font_size = axis_font_size
larva_plot.xaxis.axis_label_text_font_size = axis_font_size
larva_plot.yaxis.major_label_text_font_size = axis_tick_font_size
larva_plot.xaxis.major_label_text_font_size = axis_tick_font_size
larva_plot.ygrid.grid_line_width = grid_line_width
larva_plot.xgrid.grid_line_width = grid_line_width

pupa_plot = plt.figure(plot_height=plot_height,
                        plot_width=plot_width)
pupa_plot.title.text = 'Pupa Time-Series'
pupa_plot.xaxis.axis_label = 'time (days)'
pupa_plot.yaxis.axis_label = 'population'

pupa_plot.line(pupa_resist.index, pupa_resist,
                line_width=line_width,
                color=colors[0],
                legend='Resistant Population')
pupa_plot.line(pupa_sus_0.index, pupa_sus_0,
                line_width=line_width,
                color=colors[1],
                legend='Susceptible 0% Bt Population')
pupa_plot.line(pupa_sus_70_low.index, pupa_sus_70_low,
                line_width=line_width,
                color=colors[2],
               legend='Susceptible {} Survival 70% Bt Population'.format(np.round(param.larva_prob_bt_low_ss, 3)))
pupa_plot.line(pupa_sus_70_high.index, pupa_sus_70_high,
                line_width=line_width,
                color=colors[2],
                line_dash='dashed',
               legend='Susceptible {} Survival 70% Bt Population'.format(np.round(param.larva_prob_bt_high_ss, 3)))
pupa_plot.line(pupa_sus_90_low.index, pupa_sus_90_low,
                line_width=line_width,
                color=colors[3],
               legend='Susceptible {} Survival 90% Bt Population'.format(np.round(param.larva_prob_bt_low_ss, 3)))
pupa_plot.line(pupa_sus_90_high.index, pupa_sus_90_high,
                line_width=line_width,
                color=colors[3],
                line_dash='dashed',
               legend='Susceptible {} Survival 90% Bt Population'.format(np.round(param.larva_prob_bt_high_ss, 3)))

pupa_plot.legend.location = "bottom_right"

pupa_plot.legend.label_text_font_size = legend_font_size
pupa_plot.title.text_font_size = title_font_size
pupa_plot.yaxis.axis_line_width = axis_line_width
pupa_plot.xaxis.axis_line_width = axis_line_width
pupa_plot.yaxis.axis_label_text_font_size = axis_font_size
pupa_plot.xaxis.axis_label_text_font_size = axis_font_size
pupa_plot.yaxis.major_label_text_font_size = axis_tick_font_size
pupa_plot.xaxis.major_label_text_font_size = axis_tick_font_size
pupa_plot.ygrid.grid_line_width = grid_line_width
pupa_plot.xgrid.grid_line_width = grid_line_width

layout = lay.column(
    larva_plot,
    pupa_plot
)
plt.show(layout)
#
# # layout = lay.column(
# #     resistant_sim['mean']['(0,)_larva'][runs.observed],
# #     resistant_sim['mean']['(0,)_larva'][runs.trend],
# #     resistant_sim['mean']['(0,)_larva'][runs.season],
# #     resistant_sim['mean']['(0,)_larva'][runs.resid],
# # )
# # plt.show(layout)
