import numpy

from enthought.chaco.plot import Plot, ArrayPlotData
from enthought.enable.tools.hover_tool import HoverTool
from enthought.enable.api import Component, ComponentEditor
from enthought.traits.api import Bool, Instance, Event, Type, HasTraits
from enthought.traits.ui.api import View, Item

from enthought.chaco.tools.toolbars.plot_toolbar import PlotToolbar

class ToolbarPlot(Plot):
    # Should we turn on the auto-hide feature on the toolbar?
    auto_hide = Bool(False)

    # Hover Tool - used when auto-hide is True
    hovertool = Instance(HoverTool)
    hovertool_added = False

    # Hover Toolbar - is always visible when auto-hide is False
    toolbar = Instance(PlotToolbar)
    toolbar_class = Type(PlotToolbar)
    toolbar_added = False

    def __init__(self, *args, **kw):
        super(ToolbarPlot, self).__init__(*args, **kw)

        self.hovertool = HoverTool(self, area_type="top",
                                   callback=self.add_toolbar)
        self.tools.append(self.hovertool)

        self.toolbar = self.toolbar_class(self)
        self.add_toolbar()

    def add_toolbar(self):
        if not self.toolbar_added:
            self.overlays.append(self.toolbar)
            self.toolbar_added = True
            self.request_redraw()

    def remove_toolbar(self):
        if self.toolbar_added and self.auto_hide:
            self.overlays.remove(self.toolbar)
            self.toolbar_added = False
            self.request_redraw()

    def add_hovertool(self):
        if not self.hovertool_added:
            self.tools.append(self.hovertool)
            self.hovertool_added = True

    def remove_hovertool(self):
        if self.hovertool_added:
            self.tools.remove(self.hovertool)
            self.hovertool_added = False

    def _auto_hide_changed(self, old, new):
        if self.auto_hide:
            self.remove_toolbar()
            self.add_hovertool()
        else:
            self.remove_hovertool()
            self.add_toolbar()

    def _bounds_changed(self, old, new):
        self.toolbar.do_layout(force=True)
        super(ToolbarPlot, self)._bounds_changed(old, new)

class ExamplePlotApp(HasTraits):
    plot = Instance(Plot)

    traits_view = View(Item('plot', editor=ComponentEditor(),
                            width = 600, height = 600,
                            show_label=False),
                            resizable=True)

    def __init__(self, index, series, **kw):
        super(ExamplePlotApp, self).__init__(**kw)
        plot_data = ArrayPlotData(index=index)
        plot_data.set_data('series', series)

        self.plot = ToolbarPlot(plot_data)
        self.plot.plot(('index', 'series'), color='auto')

index = numpy.arange(0.1, 10., 0.01)
demo = ExamplePlotApp(index, (100.0 + index) / (100.0 - 20*index**2 + 5.0*index**4))

if __name__== '__main__':
    demo.configure_traits()
