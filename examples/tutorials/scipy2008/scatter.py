
from numpy import linspace, sin
from enthought.chaco.api import ArrayPlotData, Plot
from enthought.enable.component_editor import ComponentEditor
from enthought.traits.api import HasTraits, Instance
from enthought.traits.ui.api import Item, View

class ScatterPlot(HasTraits):

    plot = Instance(Plot)

    traits_view = View(
            Item('plot', editor=ComponentEditor(),
                 show_label=False), 
            width=500, height=500,
            resizable=True,
            title="Chaco Plot")

    def __init__(self):
        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)
        # Create a Plot and associate it with the PlotData
        plot = Plot(plotdata)
        # Create a scatter plot in the Plot
        plot.plot(("x", "y"), type="scatter", color="blue")
        self.plot = plot

if __name__ == "__main__":
    ScatterPlot().configure_traits()

