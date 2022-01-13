"""
Implementation of a standard financial plot visualization using Chaco 
renderers and scales.
"""

# Major library imports
from numpy import abs, arange, cumprod, random

from enthought.chaco2.example_support import DemoFrame, demo_main, COLOR_PALETTE

# Enthought library imports
from enthought.enable2.api import Window

# Chaco imports
from enthought.chaco2.api import ArrayDataSource, BarPlot, DataRange1D, \
        LabelAxis, LinearMapper, VPlotContainer, PlotAxis, PlotGrid, \
        FilledLinePlot, add_default_grids, PlotLabel
from enthought.chaco2.tools.api import PanTool, SimpleZoom


class PlotFrame(DemoFrame):

    def _create_window(self):
       
        # Create the data and datasource objects
        numpoints = 500
        index = arange(numpoints)
        returns = random.lognormal(0.01, 0.1, size=numpoints)
        price = 100.0 * cumprod(returns)       
        volume = abs(random.normal(1000.0, 1500.0, size=numpoints) + 2000.0)

        time_ds = ArrayDataSource(index)
        vol_ds = ArrayDataSource(volume, sort_order="none")
        price_ds = ArrayDataSource(price, sort_order="none")

        xmapper = LinearMapper(range=DataRange1D(time_ds))
        vol_mapper = LinearMapper(range=DataRange1D(vol_ds))
        price_mapper = LinearMapper(range=DataRange1D(price_ds))

        price_plot = FilledLinePlot(index = time_ds, value = price_ds,
                                    index_mapper = xmapper,
                                    value_mapper = price_mapper,
                                    edge_color = "blue",
                                    face_color = "paleturquoise",
                                    bgcolor = "white",
                                    border_visible = True)
        add_default_grids(price_plot)
        price_plot.overlays.append(PlotAxis(price_plot, orientation='left'))
        price_plot.overlays.append(PlotAxis(price_plot, orientation='bottom'))
        price_plot.tools.append(PanTool(price_plot, constrain=True,
                                        constrain_direction="x"))
        price_plot.overlays.append(SimpleZoom(price_plot, drag_button="right",
                                              always_on=True,
                                              tool_mode="range",
                                              axis="index"))
        
        vol_plot = BarPlot(index = time_ds, value = vol_ds,
                           index_mapper = xmapper,
                           value_mapper = vol_mapper,
                           line_color = "transparent",
                           fill_color = "black",
                           bar_width = 1.0,
                           bar_width_type = "screen",
                           antialias = False,
                           height = 100,
                           resizable = "h",
                           bgcolor = "white",
                           border_visible = True)

        add_default_grids(vol_plot)
        vol_plot.underlays.append(PlotAxis(vol_plot, orientation='left'))
        vol_plot.tools.append(PanTool(vol_plot, constrain=True,
                                      constrain_direction="x"))

        container = VPlotContainer(bgcolor = "lightblue",
                                   spacing = 20, 
                                   padding = 50,
                                   fill_padding=False)
        container.add(vol_plot)
        container.add(price_plot)
        container.overlays.append(PlotLabel("Financial Plot",
                                            component=container,
                                            #font="Times New Roman 24"))
                                            font="Arial 24"))
        
        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,600), title="Financial plot example")
