
# Enthought library imports
from enthought.enable2.api import Canvas
from enthought.traits.api import Instance, Tuple

# Local, relative chaco imports
from plot_component import PlotComponent
from plot_containers import DEFAULT_DRAWING_ORDER

class PlotCanvas(Canvas):
    """ The PlotCanvas is basically like Canvas, but we inherit some behaviors
    from PlotComponent as well.  Some methods are redefined in here to
    explicitly make sure we get the right dispatch order.
    """

    #-------------------------------------------------------------------------
    # Public traits
    #-------------------------------------------------------------------------
    
    # Default size to use for resizable components placed onto us.
    default_component_size = Tuple(200, 200)

    #-------------------------------------------------------------------------
    # Inherited traits
    #-------------------------------------------------------------------------

    # Explicitly use the Chaco drawing order instead of the Enable one
    draw_order = Instance(list, args=(DEFAULT_DRAWING_ORDER,))

    # Redefine the enable-level set of layers to use "plot" instead
    # of "mainlayer".  This is the same thing that BasePlotContainer does.
    container_under_layers = Tuple("background", "image", "underlay", "plot")

    # Override the definition from Component
    use_backbuffer = False


    #-------------------------------------------------------------------------
    # Inherited methods
    #-------------------------------------------------------------------------

    def draw(self, gc, view_bounds=None, mode="default"):
        if self.view_bounds is None:
            self.view_bounds = view_bounds
        if self._layout_needed:
            self.do_layout()
        self._draw(gc, view_bounds, mode)

    def _dispatch_draw(self, layer, gc, view_bounds, mode):
        #import pdb; pdb.set_trace()
        Canvas._dispatch_draw(self, layer, gc, view_bounds, mode)

    def get_preferred_size(self, components=None):
        """ Returns the size (width,height) that is preferred for this
        components.
        """
        if self.view_bounds is not None:
            x, y, x2, y2 = self.view_bounds
        else:
            x, y, x2, y2 = self._bounding_box
        return (x2 - x + 1, y2 - y + 1)

    def _do_layout(self):
        #import pdb; pdb.set_trace()
        for component in self.components:
            if not self._should_layout(component):
                continue
            bounds = list(component.outer_bounds)
            if "h" in component.resizable:
                bounds[0] = self.default_component_size[0]
            if "v" in component.resizable:
                bounds[1] = self.default_component_size[1]
            component.outer_bounds = bounds

        for component in self.components:
            #import pdb; pdb.set_trace()
            component.do_layout()
        return

