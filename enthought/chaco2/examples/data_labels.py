#!/usr/bin/env python
"""
Draws a line plot with several points labelled.  Demonstrates how to annotate
plots.

Left-drag pans the plot.

Mousewheel up and down zooms the plot in and out.

Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular region to
zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow and
alt-right-arrow moves you forwards and backwards through the "zoom history".
"""

# Major library imports
from numpy import arange, fabs, pi
from scipy.special import jn

# Enthought library imports
from enthought.enable2.wx_backend.api import Window

# Chaco imports
from enthought.chaco2.examples import DemoFrame, demo_main, COLOR_PALETTE
from enthought.chaco2.api import create_line_plot, add_default_axes, add_default_grids, \
                                 OverlayPlotContainer, VPlotContainer, DataLabel
from enthought.chaco2.tools.api import PanTool, SimpleZoom



class PlotFrame(DemoFrame):
    def _create_window(self):
        container = OverlayPlotContainer(padding = 50, fill_padding = True,
                                         bgcolor = "lightgray", use_backbuffer=True)
        self.container = container
        
        # Create the initial X-series of data
        numpoints = 100
        low = -5
        high = 15.0
        x = arange(low, high+0.001, (high-low)/numpoints)
        y = jn(0, x)
        plot = create_line_plot((x,y), color=tuple(COLOR_PALETTE[0]), width=2.0)
        plot.index.sort_order = "ascending"
        plot.bgcolor = "white"
        plot.border_visible = True
        add_default_grids(plot)
        add_default_axes(plot)

        # Add some tools
        plot.tools.append(PanTool(plot))
        zoom = SimpleZoom(plot, tool_mode="box", always_on=False)
        plot.overlays.append(zoom)

        # Add a static label at a particular point.  Note the use of padding
        # to offset the label from its data point.
        label = DataLabel(component=plot, data_point=(x[40], y[40]),
                          label_position="top left", padding=40,
                          bgcolor = "lightgray",
                          border_visible=False)
        plot.overlays.append(label)

        label2 = DataLabel(component=plot, data_point=(x[20], y[20]),
                           label_position="bottom right",
                           border_visible=False,
                           bgcolor="transparent",
                           marker_color="blue",
                           marker_line_color="transparent",
                           marker = "diamond",
                           arrow_visible=False)
        plot.overlays.append(label2)

        label3 = DataLabel(component=plot, data_point=(x[80], y[80]),
                           label_position="top", padding_bottom=20,
                           marker_color="transparent",
                           marker_size=8,
                           marker="circle",
                           arrow_visible=False)
        plot.overlays.append(label3)
    
        container.add(plot)

        return Window(self, -1, component=container)

if __name__ == "__main__":
    demo_main(PlotFrame, size=(800,700), title="Data label example")

# EOF
