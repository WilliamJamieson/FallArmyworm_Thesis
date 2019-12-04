import bokeh.plotting as plt
import bokeh.layouts  as lay
import bokeh.palettes as palettes

import numpy  as np
import pickle as pickle

import parameters.model_parameters as param

import multi_gen.season as season
import multi_gen.runs   as runs

colors    = palettes.Colorblind[8]
save_file = 'mix_sim_90_bt_0_D_high_save.html'
plt.output_file(save_file)

plot_width  = 2000
plot_height = 600


line_width       = 3.5
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'

sim_0_file = '{}_summary.data'.format(runs.high_90[0])
sim_1_file = '{}_summary.data'.format(runs.high_90[1])
sim_2_file = '{}_summary.data'.format(runs.high_90[2])
sim_3_file = '{}_summary.data'.format(runs.high_90[3])
sim_4_file = '{}_summary.data'.format(runs.high_90[4])

with open(sim_0_file, 'rb') as read_file:
    sim_0_allele = pickle.load(read_file)
with open(sim_1_file, 'rb') as read_file:
    sim_1_allele = pickle.load(read_file)
with open(sim_2_file, 'rb') as read_file:
    sim_2_allele = pickle.load(read_file)
with open(sim_3_file, 'rb') as read_file:
    sim_3_allele = pickle.load(read_file)
with open(sim_4_file, 'rb') as read_file:
    sim_4_allele = pickle.load(read_file)

sim_0_rr = season.Seasonal.create(runs.high_90[0], 83)
sim_1_rr = season.Seasonal.create(runs.high_90[1], 73)
sim_2_rr = season.Seasonal.create(runs.high_90[2], 82)
sim_3_rr = season.Seasonal.create(runs.high_90[3], 82)
sim_4_rr = season.Seasonal.create(runs.high_90[4], 57)

sim_0_sr = season.Seasonal.create(runs.high_90[0], 83)
sim_1_sr = season.Seasonal.create(runs.high_90[1], 73)
sim_2_sr = season.Seasonal.create(runs.high_90[2], 83)
sim_3_sr = season.Seasonal.create(runs.high_90[3], 83)
sim_4_sr = season.Seasonal.create(runs.high_90[4], 83)

sim_0_ss = season.Seasonal.create(runs.high_90[0], 83)
sim_1_ss = season.Seasonal.create(runs.high_90[1], 73)
sim_2_ss = season.Seasonal.create(runs.high_90[2], 83)
sim_3_ss = season.Seasonal.create(runs.high_90[3], 83)
sim_4_ss = season.Seasonal.create(runs.high_90[4], 83)

larva_0_period = sim_0_allele[runs.summaries[0]][runs.tables[2]]
larva_1_period = sim_1_allele[runs.summaries[0]][runs.tables[2]]
larva_2_period = sim_2_allele[runs.summaries[0]][runs.tables[2]]
larva_3_period = sim_3_allele[runs.summaries[0]][runs.tables[2]]
larva_4_period = sim_4_allele[runs.summaries[0]][runs.tables[2]]

larva_0_rr = sim_0_rr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]]
larva_1_rr = sim_1_rr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]]
larva_2_rr = sim_2_rr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]]
larva_3_rr = sim_3_rr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]]
larva_4_rr = sim_4_rr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[0]]

larva_0_sr = sim_0_sr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[1]]
larva_1_sr = sim_1_sr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[1]]
larva_2_sr = sim_2_sr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[1]]
larva_3_sr = sim_3_sr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[1]]
larva_4_sr = sim_4_sr[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[1]]

larva_0_ss = sim_0_ss[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]]
larva_1_ss = sim_1_ss[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]]
larva_2_ss = sim_2_ss[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]]
larva_3_ss = sim_3_ss[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]]
larva_4_ss = sim_4_ss[runs.summaries[0]][runs.tables[2]][runs.trend][runs.columns[2]]


allele_plot = plt.figure(plot_height=plot_height,
                         plot_width=plot_width,
                         y_range=(0, 1))
allele_plot.title.text = 'Pupa Time-Series'
allele_plot.xaxis.axis_label = 'time (days)'
allele_plot.yaxis.axis_label = '% resistant'

allele_plot.line(larva_0_period.index, larva_0_period[runs.columns[3]],
                 line_width=line_width,
                 color=colors[0],
                 legend='Cannibalism:{}'.format(np.round(param.cannib_0, 3)))

allele_plot.line(larva_1_period.index, larva_1_period[runs.columns[3]],
                 line_width=line_width,
                 color=colors[1],
                 legend='Cannibalism:{}'.format(np.round(param.cannib_1, 3)))

allele_plot.line(larva_2_period.index, larva_2_period[runs.columns[3]],
                 line_width=line_width,
                 color=colors[2],
                 legend='Cannibalism:{}'.format(np.round(param.cannib_2, 3)))

allele_plot.line(larva_3_period.index, larva_3_period[runs.columns[3]],
                 line_width=line_width,
                 color=colors[3],
                 legend='Cannibalism:{}'.format(np.round(param.cannib_3, 3)))

allele_plot.line(larva_4_period.index, larva_4_period[runs.columns[3]],
                 line_width=line_width,
                 color=colors[4],
                 legend='Cannibalism:{}'.format(np.round(param.cannib_4, 3)))

allele_plot.legend.location = "bottom_right"

allele_plot.legend.label_text_font_size = legend_font_size
allele_plot.title.text_font_size = title_font_size
allele_plot.yaxis.axis_line_width = axis_line_width
allele_plot.xaxis.axis_line_width = axis_line_width
allele_plot.yaxis.axis_label_text_font_size = axis_font_size
allele_plot.xaxis.axis_label_text_font_size = axis_font_size
allele_plot.yaxis.major_label_text_font_size = axis_tick_font_size
allele_plot.xaxis.major_label_text_font_size = axis_tick_font_size
allele_plot.ygrid.grid_line_width = grid_line_width
allele_plot.xgrid.grid_line_width = grid_line_width


pupa_plot = plt.figure(plot_height=plot_height,
                       plot_width=plot_width)
pupa_plot.title.text = 'Pupa Time-Series'
pupa_plot.xaxis.axis_label = 'time (days)'
pupa_plot.yaxis.axis_label = 'population'

pupa_plot.line(larva_0_rr.index, larva_0_rr,
# pupa_plot.line(larva_0_period.index, larva_0_period[runs.columns[0]],
               line_width=line_width,
               color=colors[0],
               legend='Resistant Cannibalism:{}'.format(np.round(param.cannib_0, 3)))
pupa_plot.line(larva_0_sr.index, larva_0_sr,
# pupa_plot.line(larva_0_period.index, larva_0_period[runs.columns[1]],
               line_width=line_width,
               color=colors[0],
               line_dash='dotted',
               legend='Heterozygous Cannibalism:{}'.format(np.round(param.cannib_0, 3)))
pupa_plot.line(larva_0_ss.index, larva_0_ss,
# pupa_plot.line(larva_0_period.index, larva_0_period[runs.columns[2]],
               line_width=line_width,
               color=colors[0],
               line_dash='dashed',
               legend='Susceptible Cannibalism:{}'.format(np.round(param.cannib_0, 3)))

pupa_plot.line(larva_1_rr.index, larva_1_rr,
# pupa_plot.line(larva_1_period.index, larva_1_period[runs.columns[0]],
               line_width=line_width,
               color=colors[1],
               legend='Resistant Cannibalism:{}'.format(np.round(param.cannib_1, 3)))
pupa_plot.line(larva_1_sr.index, larva_1_sr,
# pupa_plot.line(larva_1_period.index, larva_1_period[runs.columns[1]],
               line_width=line_width,
               color=colors[1],
               line_dash='dotted',
               legend='Heterozygous Cannibalism:{}'.format(np.round(param.cannib_1, 3)))
pupa_plot.line(larva_1_ss.index, larva_1_ss,
# pupa_plot.line(larva_1_period.index, larva_1_period[runs.columns[2]],
               line_width=line_width,
               color=colors[1],
               line_dash='dashed',
               legend='Susceptible Cannibalism:{}'.format(np.round(param.cannib_1, 3)))

pupa_plot.line(larva_2_rr.index, larva_2_rr,
# pupa_plot.line(larva_2_period.index, larva_2_period[runs.columns[0]],
               line_width=line_width,
               color=colors[2],
               legend='Resistant Cannibalism:{}'.format(np.round(param.cannib_2, 3)))
pupa_plot.line(larva_2_sr.index, larva_2_sr,
# pupa_plot.line(larva_2_period.index, larva_2_period[runs.columns[1]],
               line_width=line_width,
               color=colors[2],
               line_dash='dotted',
               legend='Heterozygous Cannibalism:{}'.format(np.round(param.cannib_2, 3)))
pupa_plot.line(larva_2_ss.index, larva_2_ss,
# pupa_plot.line(larva_2_period.index, larva_2_period[runs.columns[2]],
               line_width=line_width,
               color=colors[2],
               line_dash='dashed',
               legend='Susceptible Cannibalism:{}'.format(np.round(param.cannib_2, 3)))

pupa_plot.line(larva_3_rr.index, larva_3_rr,
# pupa_plot.line(larva_3_period.index, larva_3_period[runs.columns[0]],
               line_width=line_width,
               color=colors[3],
               legend='Resistant Cannibalism:{}'.format(np.round(param.cannib_3, 3)))
pupa_plot.line(larva_3_sr.index, larva_3_sr,
# pupa_plot.line(larva_3_period.index, larva_3_period[runs.columns[1]],
               line_width=line_width,
               color=colors[3],
               line_dash='dotted',
               legend='Heterozygous Cannibalism:{}'.format(np.round(param.cannib_3, 3)))
pupa_plot.line(larva_3_ss.index, larva_3_ss,
# pupa_plot.line(larva_3_period.index, larva_3_period[runs.columns[2]],
               line_width=line_width,
               color=colors[3],
               line_dash='dashed',
               legend='Susceptible Cannibalism:{}'.format(np.round(param.cannib_3, 3)))

pupa_plot.line(larva_4_rr.index, larva_4_rr,
# pupa_plot.line(larva_4_period.index, larva_4_period[runs.columns[0]],
               line_width=line_width,
               color=colors[4],
               legend='Resistant Cannibalism:{}'.format(np.round(param.cannib_4, 3)))
pupa_plot.line(larva_4_sr.index, larva_4_sr,
# pupa_plot.line(larva_4_period.index, larva_4_period[runs.columns[1]],
               line_width=line_width,
               color=colors[4],
               line_dash='dotted',
               legend='Heterozygous Cannibalism:{}'.format(np.round(param.cannib_4, 3)))
pupa_plot.line(larva_4_ss.index, larva_4_ss,
# pupa_plot.line(larva_4_period.index, larva_4_period[runs.columns[2]],
               line_width=line_width,
               color=colors[4],
               line_dash='dashed',
               legend='Susceptible Cannibalism:{}'.format(np.round(param.cannib_4, 3)))

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

layout = lay.column(allele_plot,
                    pupa_plot)

plt.show(layout)
