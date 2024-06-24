""" Defines a the DragZoom tool class
"""

# Enthought library imports
from enthought.traits.api import Bool, Enum, Float, Tuple

# Chaco imports
from base_zoom_tool import BaseZoomTool
from drag_tool import DragTool


class DragZoom(DragTool, BaseZoomTool):
    """ A zoom tool that zooms continuously with a mouse drag movement, instead
    of using a zoom box or range.

    By default, the tool maintains aspect ratio and zooms the plot's X and Y
    axes by the same amount as the user drags up and down.  (In this default
    configuration, the horizontal position of the drag motion has no effect.)

    By setting **maintain_aspect_ratio** to False, this tool will separably zoom
    the X and Y axis ranges by the (possibly different) horizontal and vertical 
    drag motions.  This is similar to the drag zoom interaction in Matplotlib.
    """

    # The mouse button that initiates the drag
    drag_button = Enum("left", "right", "middle")

    # Scaling factor on the zoom "speed".  A speed of 1.0 implies a zoom rate of
    # 5% for every 10 pixels.
    speed = Float(1.0)

    # Whether or not to preserve the aspect ratio of X to Y while zooming in.
    # (See class docstring for more info.)
    maintain_aspect_ratio = Bool(True)

    # The pointer to use when we're in the act of zooming
    drag_pointer = "magnifier"


    #------------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------------

    # (x,y) of the point where the mouse button was pressed.
    _original_xy = Tuple()
    
    # Data coordinates of **_original_xy**.  This may be either (index,value)
    # or (value,index) depending on the component's orientation.
    _original_data = Tuple()

    # A tuple of ((x,y), (x2,y2)) of the original, unzoomed screen bounds
    _orig_screen_bounds = Tuple()

    # The x and y positions of the previous mouse event.  The zoom rate is
    # based on the percentage change in position between the previous position
    # and the current mouse position, possibly in both axes.
    _prev_x = Float()
    _prev_y = Float()

    def __init__(self, component=None, *args, **kw):
        super(DragZoom, self).__init__(component, *args, **kw)
        c = component
        if c is not None:
            self._orig_screen_bounds = ((c.x, c.y), (c.x2, c.y2))

    def dragging(self, event):

        # Compute the zoom amount based on the pixel difference between
        # the previous mouse event and the current one.
        if self.maintain_aspect_ratio:
            zoom_x = zoom_y = self._calc_zoom(self._prev_y, event.y)
        else:
            zoom_x = self._calc_zoom(self._prev_x, event.x)
            zoom_y = self._calc_zoom(self._prev_y, event.y)

        c = self.component
        low_pt, high_pt = self._map_coordinate_box((c.x, c.y), (c.x2, c.y2))

        # The original screen bounds are used to test if we've reached max_zoom
        orig_low, orig_high = self._orig_screen_bounds

        datarange_list = [(0, c.x_mapper.range, zoom_x), (1, c.y_mapper.range, zoom_y)]
        for ndx, datarange, zoom in datarange_list:
            mouse_val = self._original_data[ndx]
            newlow = mouse_val - zoom * (mouse_val - low_pt[ndx])
            newhigh = mouse_val + zoom * (high_pt[ndx] - mouse_val)
            
            ol, oh = orig_low[ndx], orig_high[ndx]
            if self._zoom_limit_reached(ol, oh, newlow, newhigh):
                event.handled = True
                return
            
            datarange.set_bounds(newlow, newhigh)
       
        self._prev_y = event.y
        self._prev_x = event.x
        event.handled = True
        self.component.request_redraw()
        return

    def drag_start(self, event, capture_mouse=True):
        self._original_xy = (event.x, event.y)
        c = self.component
        self._orig_screen_bounds = ((c.x,c.y), (c.x2,c.y2))
        self._original_data = (c.x_mapper.map_data(event.x), c.y_mapper.map_data(event.y))
        self._prev_x = event.x
        self._prev_y = event.y
        if capture_mouse:
            event.window.set_pointer(self.drag_pointer)
            event.window.set_mouse_owner(self, event.net_transform())
        event.handled = True
        return

    def drag_end(self, event):
        event.window.set_pointer("arrow")
        if event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)
        event.handled = True
        return

    def _calc_zoom(self, original, clicked):
        """ Returns the amount to scale the range based on the original 
        cursor position and a new, updated position.
        """
        # We express the built-in zoom scaling as 0.05/10 to indicate a scaling
        # of 5% every 10 pixels, per the docstring for the 'speed' trait.
        return 1.0 - self.speed * (clicked - original) * (0.05/10)

