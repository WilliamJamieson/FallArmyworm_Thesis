import bokeh.plotting as plt
import bokeh.palettes as palettes

import multi_gen.error_data as error
import multi_gen.runs   as runs

colors    = palettes.Colorblind[8]
save_file = 'resistant_sim_error_plots.html'
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


sim = error.ProcessData(runs.runs[0]).series()

egg    = sim[runs.tables[0]][runs.columns[0]]
larva  = sim[runs.tables[1]][runs.columns[0]]
pupa   = sim[runs.tables[2]][runs.columns[0]]
female = sim[runs.tables[3]][runs.columns[0]]

reg_plot = plt.figure(plot_height=plot_height,
                      plot_width=plot_width)
reg_plot.title.text = 'Resistant Error'
reg_plot.xaxis.axis_label = 'trials'
reg_plot.yaxis.axis_label = 'Mean Relative Error'

reg_plot.line(list(egg.keys()), list(egg.values()),
              line_width=line_width,
              color=colors[0],
              legend='Egg')
reg_plot.line(list(larva.keys()), list(larva.values()),
              line_width=line_width,
              color=colors[1],
              legend='Larva')
reg_plot.line(list(pupa.keys()), list(pupa.values()),
              line_width=line_width,
              color=colors[2],
              legend='Pupa')
reg_plot.line(list(female.keys()), list(female.values()),
              line_width=line_width,
              color=colors[3],
              legend='Adult')

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
