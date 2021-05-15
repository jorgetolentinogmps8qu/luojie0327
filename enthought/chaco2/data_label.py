
# Enthought library imports
from enthought.traits.api import Any, Array, Bool, Enum, Float, Int, List, Tuple, Trait
from enthought.enable2.api import ColorTrait

# Local, relative imports
from scatterplot import render_markers
from scatter_markers import marker_trait
from tooltip import ToolTip


# Used to specify the position of the label relative to its target
LabelPositionTrait = Enum("top right", "bottom", "left", "right", "top left",
                         "bottom left", "bottom right", "center")

class DataLabel(ToolTip):
    """ Labels a point in data space """

    # The point in data space where this label should anchor itself
    data_point = Trait(None, None, Tuple, List, Array)

    # The location of the data label relative to the data point
    label_position = LabelPositionTrait

    # Whether or not to mark the point on the data that this label refers to
    draw_marker = Bool(True)

    # The type of marker to use.  This is a mapped trait using strings as the
    # keys.
    marker = marker_trait
    
    # The pixel size of the marker (doesn't include the thickness of the outline)
    marker_size = Int(4)
    
    # The thickness, in pixels, of the outline to draw around the marker.  If
    # this is 0, no outline will be drawn.
    marker_line_width = Float(1.0)

    # The color of the inside of the marker
    marker_color = ColorTrait("red")

    # The color out of the border drawn around the marker
    marker_line_color = ColorTrait("black")
    
    # Whether or not to draw an arrow from the label to the data point.  Only
    # used if data_point is not None.
    # FIXME: replace with some sort of ArrowStyle
    draw_arrow = Bool(True)

    # Should the label clip itself against the main plot area?  If not, then
    # the label will draw  into the padding area (where axes typically reside).
    clip_to_plot = Bool(True)

    #-------------------------------------------------------------------------
    # Private traits
    #-------------------------------------------------------------------------

    # Tuple (sx, sy) of the mapped screen coords of self.data_point
    _screen_coords = Any

    def _data_point_changed(self, old, new):
        if new is not None:
            self.lines = [str(new)]

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if self.clip_to_plot:
            gc.save_state()
            c = component
            gc.clip_to_rect(c.x, c.y, c.width, c.height)

        # layout and render the label itself
        ToolTip.overlay(self, component, gc, view_bounds, mode)

        # draw the arrow if necessary
        if self.draw_arrow:
            print "draw_arrow is not yet implemented"

        # draw the marker
        if self.draw_marker:
            render_markers(gc, [self._screen_coords], self.marker, self.marker_size,
                           self.marker_color_, self.marker_line_width, self.marker_line_color_)

        if self.clip_to_plot:
            gc.restore_state()

    def _do_layout(self, size=None):
        if not self.component or not hasattr(self.component, "map_screen"):
            return
        ToolTip._do_layout(self)

        self._screen_coords = self.component.map_screen(self.data_point)
        sx, sy = self._screen_coords
        orientation = self.label_position
        if ("left" in orientation) or ("right" in orientation):
            if " " not in orientation:
                self.outer_y = sy
            if "left" in orientation:
                self.outer_x = sx - self.outer_width - 1
            elif "right" in orientation:
                self.outer_x = sx
        if ("top" in orientation) or ("bottom" in orientation):
            if " " not in orientation:
                self.outer_x = sx
            if "bottom" in orientation:
                self.outer_y = sy - self.outer_height - 1
            elif "top" in orientation:
                self.outer_y = sy
        if orientation == "center":
            self.x = sx - (self.width/2)
            self.y = sy - (self.height/2)
        return
