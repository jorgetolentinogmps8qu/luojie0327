"""
Draws a vector or "quiver" plot of a set of random points.
 - Left-drag pans the plot.
 - Mousewheel up and down zooms the plot in and out.
 - Pressing "z" brings up the Zoom Box, and you can click-drag a rectangular
   region to zoom.  If you use a sequence of zoom boxes, pressing alt-left-arrow
   and alt-right-arrow moves you forwards and backwards through the "zoom
   history".
"""

# Major library imports
from numpy import array, sort
from numpy.random import random

# Enthought library imports
from enable.api import Component, ComponentEditor
from traits.api import HasTraits, Instance, Int
from traitsui.api import Item, View

# Chaco imports
from chaco.api import ArrayDataSource, MultiArrayDataSource, DataRange1D, \
        LinearMapper, QuiverPlot, OverlayPlotContainer, add_default_grids, \
        add_default_axes
from chaco.tools.api import PanTool, ZoomTool


class PlotExample(HasTraits):
    plot = Instance(Component)
    numpts = Int(400)
    vectorlen = Int(15)

    traits_view = View(Item('plot', editor=ComponentEditor(), show_label=False),
                       width=600, height=600)

    def _plot_default(self):
        # Create starting points for the vectors.
        numpts = self.numpts
        x = sort(random(numpts))
        y = random(numpts)

        # Create vectors.
        vectorlen = self.vectorlen
        vectors = array((random(numpts)*vectorlen, random(numpts)*vectorlen)).T

        # Create an array data sources to plot all vectors at once
        xs = ArrayDataSource(x, sort_order='ascending')
        ys = ArrayDataSource(y)
        vector_ds = MultiArrayDataSource(vectors)

        # Set up the Plot
        xrange = DataRange1D()
        xrange.add(xs)
        yrange = DataRange1D()
        yrange.add(ys)

        quiverplot = QuiverPlot(index = xs, value = ys,
                        vectors = vector_ds,
                        index_mapper = LinearMapper(range=xrange),
                        value_mapper = LinearMapper(range=yrange),
                        bgcolor = "white")

        add_default_axes(quiverplot)
        add_default_grids(quiverplot)

        # Attach some tools to the plot
        quiverplot.tools.append(PanTool(quiverplot, constrain_key="shift"))
        zoom = ZoomTool(quiverplot)
        quiverplot.overlays.append(zoom)

        container = OverlayPlotContainer(quiverplot, padding=50)

        return container


demo = PlotExample()

if __name__ == "__main__":
    demo.configure_traits()
