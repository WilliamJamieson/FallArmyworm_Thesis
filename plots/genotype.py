import datetime
import collections  as collect
import dataclasses  as dclass
import numpy        as np

import bokeh.plotting as plt
import bokeh.models   as mdl
import bokeh.layouts  as lay
import bokeh.palettes as palettes

import parameters.data_tracking    as tracking
import parameters.model_parameters as param

import models.forage       as forage
import models.graph        as graph
import models.growth       as growth
import models.init_biomass as init_bio
import models.movement     as move
import models.reproduction as repro

import source.hint    as hint
import source.keyword as keyword

import source.agents.egg_mass as egg_mass


num = 100000


line_width       = 2
point_size       = 10
point_size_stoch = 8

axis_line_width     = 2
grid_line_width     = 2
title_font_size     = '16pt'
legend_font_size    = '12pt'
axis_font_size      = '12pt'
axis_tick_font_size = '10pt'


plot_width  = 800
plot_height = 500

colors    = palettes.Colorblind[8]
save_file = 'genotype_plots.html'

plt.output_file(save_file)


@dclass.dataclass
class Simulator(object):
    """
    Class to handle the simulation of data

    Variables:
        mother: mother's genotype
        father: father's genotype

        egg_mass: egg_mass which handles genotype crossing
    """

    mother: str
    father: str

    egg_mass: hint.egg_mass = None

    def __post_init__(self):

        if self.egg_mass is None:
            eggs          = egg_mass.Eggs({}, 0)
            # noinspection PyTypeChecker
            self.egg_mass = egg_mass.EggMass(keyword.egg_mass,
                                             '0', None, None, True, eggs)

    def get_genotypes(self, number: int) -> hint.genotypes:
        """
        Get generate number of genotypes from parents

        Args:
            number: the number of genotypes to generate

        Returns:
            list of new genotypes
        """

        return self.egg_mass.genotypes(number, self.mother, self.father)

    def get_data(self, number: int) -> dict:
        """
        Get counts of the number of generated genotypes

        Args:
            number: number of genotypes to generate

        Returns:
            counter dict
        """

        genotypes = self.get_genotypes(number)

        return collect.Counter(genotypes)

    def get_prop(self, number: int) -> dict:
        """
        Get the proportion of each genotype

        Args:
            number: number of genotypes to generate

        Returns:
            dict of proportions
        """

        counts = self.get_data(number)

        prop = {}

        if keyword.homo_r in counts:
            prop[keyword.homo_r] = counts[keyword.homo_r]/number
        else:
            prop[keyword.homo_r] = 0

        if keyword.hetero in counts:
            prop[keyword.hetero] = counts[keyword.hetero]/number
        else:
            prop[keyword.hetero] = 0

        if keyword.homo_s in counts:
            prop[keyword.homo_s] = counts[keyword.homo_s]/number
        else:
            prop[keyword.homo_s] = 0

        return prop

    @classmethod
    def run(cls, number: int,
                 mother: str,
                 father: str) -> dict:
        """
        Get the intervals of the total for each genotype

        Args:
            number: number of genotypes to generate
            mother: the mother's genotype
            father: the father's genotype

        Returns:
            dict of interval end
        """

        sim = cls(mother, father)

        prop = sim.get_prop(number)

        homo_s_end = prop[keyword.homo_s]
        hetero_end = homo_s_end + prop[keyword.hetero]
        homo_r_end = hetero_end + prop[keyword.homo_r]

        return {
            keyword.homo_s: (0,          homo_s_end),
            keyword.hetero: (homo_s_end, hetero_end),
            keyword.homo_r: (hetero_end, homo_r_end)
        }


cats = [
    'SS x SS',
    'SS x SR',
    'SS x RR',
    'SR x SR',
    'SR x RR',
    'RR x RR',
]

ss_x_ss = Simulator.run(num, keyword.homo_s, keyword.homo_s)
ss_x_sr = Simulator.run(num, keyword.homo_s, keyword.hetero)
ss_x_rr = Simulator.run(num, keyword.homo_s, keyword.homo_r)
sr_x_sr = Simulator.run(num, keyword.hetero, keyword.hetero)
sr_x_rr = Simulator.run(num, keyword.hetero, keyword.homo_r)
rr_x_rr = Simulator.run(num, keyword.homo_r, keyword.homo_r)

ss_bar_start = [
    ss_x_ss[keyword.homo_s][0],
    ss_x_sr[keyword.homo_s][0],
    ss_x_rr[keyword.homo_s][0],
    sr_x_sr[keyword.homo_s][0],
    sr_x_rr[keyword.homo_s][0],
    rr_x_rr[keyword.homo_s][0]
]
ss_bar_end = [
    ss_x_ss[keyword.homo_s][1],
    ss_x_sr[keyword.homo_s][1],
    ss_x_rr[keyword.homo_s][1],
    sr_x_sr[keyword.homo_s][1],
    sr_x_rr[keyword.homo_s][1],
    rr_x_rr[keyword.homo_s][1]
]
sr_bar_start = [
    ss_x_ss[keyword.hetero][0],
    ss_x_sr[keyword.hetero][0],
    ss_x_rr[keyword.hetero][0],
    sr_x_sr[keyword.hetero][0],
    sr_x_rr[keyword.hetero][0],
    rr_x_rr[keyword.hetero][0]
]
sr_bar_end = [
    ss_x_ss[keyword.hetero][1],
    ss_x_sr[keyword.hetero][1],
    ss_x_rr[keyword.hetero][1],
    sr_x_sr[keyword.hetero][1],
    sr_x_rr[keyword.hetero][1],
    rr_x_rr[keyword.hetero][1]
]
rr_bar_start = [
    ss_x_ss[keyword.homo_r][0],
    ss_x_sr[keyword.homo_r][0],
    ss_x_rr[keyword.homo_r][0],
    sr_x_sr[keyword.homo_r][0],
    sr_x_rr[keyword.homo_r][0],
    rr_x_rr[keyword.homo_r][0]
]
rr_bar_end = [
    ss_x_ss[keyword.homo_r][1],
    ss_x_sr[keyword.homo_r][1],
    ss_x_rr[keyword.homo_r][1],
    sr_x_sr[keyword.homo_r][1],
    sr_x_rr[keyword.homo_r][1],
    rr_x_rr[keyword.homo_r][1]
]

line_25 = mdl.Span(location=0.25,
                   dimension='width',
                   line_color='black',
                   line_width=line_width,
                   line_dash='dotted')
line_50 = mdl.Span(location=0.50,
                   dimension='width',
                   line_color='black',
                   line_width=line_width,
                   line_dash='dotted')
line_75 = mdl.Span(location=0.75,
                   dimension='width',
                   line_color='black',
                   line_width=line_width,
                   line_dash='dotted')

genotype_plot = plt.figure(plot_width=plot_width,
                           plot_height=plot_height,
                           x_range=cats)
genotype_plot.title.text = 'Genotype Proportions, Number of Trials: {}'.\
    format(num)
genotype_plot.xaxis.axis_label = 'parental cross'
genotype_plot.yaxis.axis_label = 'proportion of population'

genotype_plot.add_layout(line_25)
genotype_plot.add_layout(line_50)
genotype_plot.add_layout(line_75)

genotype_plot.vbar(cats, 0.7, ss_bar_start, ss_bar_end,
                   line_color='black', line_width=line_width,
                   fill_color=colors[0],
                   legend='SS')
genotype_plot.vbar(cats, 0.7, sr_bar_start, sr_bar_end,
                   line_color='black', line_width=line_width,
                   fill_color=colors[2],
                   legend='SR')
genotype_plot.vbar(cats, 0.7, rr_bar_start, rr_bar_end,
                   line_color='black', line_width=line_width,
                   fill_color=colors[1],
                   legend='RR')

genotype_plot.title.text_font_size = title_font_size
genotype_plot.legend.label_text_font_size = legend_font_size
genotype_plot.yaxis.axis_line_width = axis_line_width
genotype_plot.xaxis.axis_line_width = axis_line_width
genotype_plot.yaxis.axis_label_text_font_size = axis_font_size
genotype_plot.xaxis.axis_label_text_font_size = axis_font_size
genotype_plot.yaxis.major_label_text_font_size = axis_tick_font_size
genotype_plot.xaxis.major_label_text_font_size = axis_tick_font_size
genotype_plot.ygrid.grid_line_width = grid_line_width
genotype_plot.xgrid.grid_line_width = grid_line_width

plt.show(genotype_plot)
