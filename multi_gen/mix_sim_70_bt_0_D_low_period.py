import bokeh.plotting     as plt
import bokeh.models       as mdl
import bokeh.palettes     as palettes
import bokeh.models.tools as tools

import numpy as np

import parameters.model_parameters as param

import multi_gen.period as period
import multi_gen.runs   as runs

colors    = palettes.Colorblind[8]
save_file = 'mix_sim_90_bt_0_D_low_period.html'
plt.output_file(save_file)

plot_width  = 800
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


sim_0 = period.Periodogram.create(runs.low_70[0])
sim_1 = period.Periodogram.create(runs.low_70[1])
sim_2 = period.Periodogram.create(runs.low_70[2])
sim_3 = period.Periodogram.create(runs.low_70[3])
sim_4 = period.Periodogram.create(runs.low_70[4])

source_0 = mdl.ColumnDataSource(sim_0[runs.summaries[0]][runs.tables[2]][runs.columns[0]])
source_1 = mdl.ColumnDataSource(sim_1[runs.summaries[0]][runs.tables[2]][runs.columns[0]])
source_2 = mdl.ColumnDataSource(sim_2[runs.summaries[0]][runs.tables[2]][runs.columns[0]])
source_3 = mdl.ColumnDataSource(sim_3[runs.summaries[0]][runs.tables[2]][runs.columns[0]])
source_4 = mdl.ColumnDataSource(sim_4[runs.summaries[0]][runs.tables[2]][runs.columns[0]])


reg_plot = plt.figure(plot_height=plot_height,
                      plot_width=plot_width)
reg_plot.title.text = 'Periodogram 90% Bt, {} Survival'.\
    format(np.round(param.larva_prob_bt_low_ss, 3))
reg_plot.xaxis.axis_label = 'Frequency'
reg_plot.yaxis.axis_label = 'Power Spectral Density'

# reg_plot.line(x=runs.freq, y=runs.power, source=source_0,
#               line_width=line_width,
#               color=colors[0],
#               legend='Cannibalism: {}'.format(np.round(param.cannib_0, 3)))

# reg_plot.line(x=runs.freq, y=runs.power, source=source_1,
#               line_width=line_width,
#               color=colors[1],
#               legend='Cannibalism: {}'.format(np.round(param.cannib_1, 3)))

# reg_plot.line(x=runs.freq, y=runs.power, source=source_2,
#               line_width=line_width,
#               color=colors[2],
#               legend='Cannibalism: {}'.format(np.round(param.cannib_2, 3)))

# reg_plot.line(x=runs.freq, y=runs.power, source=source_3,
#               line_width=line_width,
#               color=colors[3],
#               legend='Cannibalism: {}'.format(np.round(param.cannib_3, 3)))

reg_plot.line(x=runs.freq, y=runs.power, source=source_4,
              line_width=line_width,
              color=colors[4],
              legend='Cannibalism: {}'.format(np.round(param.cannib_4, 3)))

reg_hover = tools.HoverTool()
reg_hover.tooltips = [
    ('Frequency', '@freq'),
    ('Period', '@period'),
    ('Spectral Density', '@power'),
    ('Genotype', '@genotype'),
    ('Source', '@comb')
]
reg_plot.add_tools(reg_hover)


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

