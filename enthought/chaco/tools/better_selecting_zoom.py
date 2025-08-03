import numpy

from enthought.chaco.abstract_overlay import AbstractOverlay
from enthought.enable.api import ColorTrait
from enthought.traits.api import Bool, Enum, Trait, Int, Float, Tuple

from better_zoom import BetterZoom, ZoomState

class SelectedZoomState(ZoomState):
    def apply(self, zoom_tool):
        x_mapper = zoom_tool._get_x_mapper()
        y_mapper = zoom_tool._get_y_mapper()
        
        x_mapper.range.low = self.next[0]
        x_mapper.range.high = self.next[1]
        y_mapper.range.low = self.next[2]
        y_mapper.range.high = self.next[3]
        
    def revert(self, zoom_tool):
        x_mapper = zoom_tool._get_x_mapper()
        y_mapper = zoom_tool._get_y_mapper()
        
        x_mapper.range.low = self.prev[0]
        x_mapper.range.high = self.prev[1]
        y_mapper.range.low = self.prev[2]
        y_mapper.range.high = self.prev[3]

class BetterSelectingZoom(AbstractOverlay, BetterZoom):
    """ Zooming tool which allows the user to draw a box which defines the 
        desired region to zoom in to
    """
    
    # The selection mode:
    #
    # range:
    #   Select a range across a single index or value axis.
    # box:
    #   Perform a "box" selection on two axes.
    tool_mode = Enum("box", "range")

    # Is the tool always "on"? If True, left-clicking always initiates
    # a zoom operation; if False, the user must press a key to enter zoom mode.
    always_on = Bool(False)

    # Defines a meta-key, that works with always_on to set the zoom mode. This
    # is useful when the zoom tool is used in conjunction with the pan tool.
    always_on_modifier = Enum('control', 'shift', 'control', 'alt')

    # The mouse button that initiates the drag.  If "None", then the tool
    # will not respond to drag.  (It can still respond to mousewheel events.)
    drag_button = Enum("left", "right", None)

    # The minimum amount of screen space the user must select in order for
    # the tool to actually take effect.
    minimum_screen_delta = Int(10)

    #-------------------------------------------------------------------------
    # Appearance properties (for Box mode)
    #-------------------------------------------------------------------------

    # The pointer to use when drawing a zoom box.
    pointer = "magnifier"

    # The color of the selection box.
    color = ColorTrait("lightskyblue")

    # The alpha value to apply to **color** when filling in the selection
    # region.  Because it is almost certainly useless to have an opaque zoom
    # rectangle, but it's also extremely useful to be able to use the normal
    # named colors from Enable, this attribute allows the specification of a
    # separate alpha value that replaces the alpha value of **color** at draw
    # time.
    alpha = Trait(0.4, None, Float)

    # The color of the outside selection rectangle.
    border_color = ColorTrait("dodgerblue")

    # The thickness of selection rectangle border.
    border_size = Int(1)

    # The possible event states of this zoom tool.
    event_state = Enum("normal", "selecting")
    
    # The (x,y) screen point where the mouse went down.
    _screen_start = Trait(None, None, Tuple)

    # The (x,,y) screen point of the last seen mouse move event.
    _screen_end = Trait(None, None, Tuple)
    
    
    def __init__(self, component=None, *args, **kw):
        # Since this class uses multiple inheritance (eek!), lets be
        # explicit about the order of the parent class constructors
        AbstractOverlay.__init__(self, component, *args, **kw)
        BetterZoom.__init__(self, component, *args, **kw)
        
    def reset(self, event=None):
        """ Resets the tool to normal state, with no start or end position.
        """
        self.event_state = "normal"
        self._screen_start = None
        self._screen_end = None
    
    #--------------------------------------------------------------------------
    #  BetterZoom interface
    #--------------------------------------------------------------------------
    
    def normal_left_down(self, event):
        """ Handles the left mouse button being pressed while the tool is
        in the 'normal' state.

        If the tool is enabled or always on, it starts selecting.
        """
        if self._is_enabling_event(event):
            self._start_select(event)
            event.handled = True

        return

    def normal_right_down(self, event):
        """ Handles the right mouse button being pressed while the tool is
        in the 'normal' state.

        If the tool is enabled or always on, it starts selecting.
        """
        if self._is_enabling_event(event):
            self._start_select(event)
            event.handled = True

        return
    
    def selecting_mouse_move(self, event):
        """ Handles the mouse moving when the tool is in the 'selecting' state.

        The selection is extended to the current mouse position.
        """
        self._screen_end = (event.x, event.y)
        self.component.request_redraw()
        event.handled = True
        return

    def selecting_left_up(self, event):
        """ Handles the left mouse button being released when the tool is in
        the 'selecting' state.

        Finishes selecting and does the zoom.
        """
        if self.drag_button == "left":
            self._end_select(event)
        return

    def selecting_right_up(self, event):
        """ Handles the right mouse button being released when the tool is in
        the 'selecting' state.

        Finishes selecting and does the zoom.
        """
        if self.drag_button == "right":
            self._end_select(event)
        return

    def selecting_mouse_leave(self, event):
        """ Handles the mouse leaving the plot when the tool is in the
        'selecting' state.

        Ends the selection operation without zooming.
        """
        self._end_selecting(event)
        return
    
    #--------------------------------------------------------------------------
    #  AbstractOverlay interface
    #--------------------------------------------------------------------------
    
    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        """ Draws this component overlaid on another component.

        Overrides AbstractOverlay.
        """
        if self.event_state == "selecting":
            if self.tool_mode == "range":
                self._overlay_range(component, gc)
            else:
                self._overlay_box(component, gc)
        return

    #--------------------------------------------------------------------------
    #  private interface
    #--------------------------------------------------------------------------

    def _is_enabling_event(self, event):
        if self.always_on:
            enabled = True
        else:
            if self.always_on_modifier == 'shift':
                enabled = event.shift_down
            elif self.always_on_modifier == 'control':
                enabled = event.control_down
            elif self.always_on_modifier == 'alt':
                enabled = event.alt_down
            
        if enabled:
            if event.right_down and self.drag_button == 'right':
                return True
            if event.left_down and self.drag_button == 'left':
                return True

        return False

    def _start_select(self, event):
        """ Starts selecting the zoom region
        """
        if self.component.active_tool in (None, self):
            self.component.active_tool = self
        else:
            self._enabled = False
        self._screen_start = (event.x, event.y)
        self._screen_end = None
        self.event_state = "selecting"
        event.window.set_pointer(self.pointer)
        event.window.set_mouse_owner(self, event.net_transform())
        self.selecting_mouse_move(event)
        return

    def _end_select(self, event):
        """ Ends selection of the zoom region, adds the new zoom range to
        the zoom stack, and does the zoom.
        """
        self._screen_end = (event.x, event.y)

        start = numpy.array(self._screen_start)
        end = numpy.array(self._screen_end)

        if sum(abs(end - start)) < self.minimum_screen_delta:
            self._end_selecting(event)
            event.handled = True
            return
        
        low, high = self._map_coordinate_box(self._screen_start, self._screen_end)

        x_range = self._get_x_mapper().range
        y_range = self._get_y_mapper().range  
        
        prev = (x_range.low, x_range.high, y_range.low, y_range.high)           
        
        if self.tool_mode == 'range':
            axis = self._determine_axis()
            if axis == 1:
                # vertical
                next = (x_range.low, x_range.high, low[1], high[1])
            else:
                # horizontal
                next = (low[0], high[0], y_range.low, y_range.high)
            
        else:
            next = (low[0], high[0], low[1], high[1]) 
            
        zoom_state = SelectedZoomState(prev, next)            
        zoom_state.apply(self)
        self._append_state(zoom_state)
        
        self._end_selecting(event)
        event.handled = True
        return

    def _end_selecting(self, event=None):
        """ Ends selection of zoom region, without zooming.
        """
        self.reset()
        self._enabled = False
        if self.component.active_tool == self:
            self.component.active_tool = None
        if event and event.window:
            event.window.set_pointer("arrow")
        
        self.component.request_redraw()
        if event and event.window.mouse_owner == self:
            event.window.set_mouse_owner(None)
        return

    def _overlay_box(self, component, gc):
        """ Draws the overlay as a box.
        """
        if self._screen_start and self._screen_end:
            gc.save_state()
            try:
                gc.set_antialias(0)
                gc.set_line_width(self.border_size)
                gc.set_stroke_color(self.border_color_)
                gc.clip_to_rect(component.x, component.y, component.width, component.height)
                x, y = self._screen_start
                x2, y2 = self._screen_end
                rect = (x, y, x2-x+1, y2-y+1)
                if self.color != "transparent":
                    if self.alpha:
                        color = list(self.color_)
                        if len(color) == 4:
                            color[3] = self.alpha
                        else:
                            color += [self.alpha]
                    else:
                        color = self.color_
                    gc.set_fill_color(color)
                    gc.rect(*rect)
                    gc.draw_path()
                else:
                    gc.rect(*rect)
                    gc.stroke_path()
            finally:
                gc.restore_state()
        return

    def _overlay_range(self, component, gc):
        """ Draws the overlay as a range.
        """
        axis_ndx = self._determine_axis()
        lower_left = [0,0]
        upper_right = [0,0]
        lower_left[axis_ndx] = self._screen_start[axis_ndx]
        lower_left[1-axis_ndx] = self.component.position[1-axis_ndx]
        upper_right[axis_ndx] = self._screen_end[axis_ndx] - self._screen_start[axis_ndx]
        upper_right[1-axis_ndx] = self.component.bounds[1-axis_ndx]

        gc.save_state()
        try:
            gc.set_antialias(0)
            gc.set_alpha(self.alpha)
            gc.set_fill_color(self.color_)
            gc.set_stroke_color(self.border_color_)
            gc.clip_to_rect(component.x, component.y, component.width, component.height)
            gc.rect(lower_left[0], lower_left[1], upper_right[0], upper_right[1])
            gc.draw_path()
        finally:
            gc.restore_state()
        return
    
    def _determine_axis(self):
        """ Determines whether the index of the coordinate along the axis of
        interest is the first or second element of an (x,y) coordinate tuple.
        """
        if self.axis == "index":
            if self.component.orientation == "h":
                return 0
            else:
                return 1
        else:
            if self.component.orientation == "h":
                return 1
            else:
                return 0

    def _map_coordinate_box(self, start, end):
        """ Given start and end points in screen space, returns corresponding
        low and high points in data space.
        """
        low = [0,0]
        high = [0,0]
        for axis_index, mapper in [(0, self.component.x_mapper), \
                                   (1, self.component.y_mapper)]:
            low_val = mapper.map_data(start[axis_index])
            high_val = mapper.map_data(end[axis_index])
            
            if low_val > high_val:
                low_val, high_val = high_val, low_val
            low[axis_index] = low_val
            high[axis_index] = high_val
        return low, high
    
