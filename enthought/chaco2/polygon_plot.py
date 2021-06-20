""" Defines the PolygonPlot class.
"""

# Standard library imports.
import logging

# Major library imports
import numpy as np

# Enthought library imports.
from enthought.enable2.api import LineStyle, black_color_trait, \
                                  transparent_color_trait
from enthought.traits.api import Float

# Local imports.
from base_xy_plot import BaseXYPlot


# Setup a logger for this module.
logger = logging.getLogger(__name__)


class PolygonPlot(BaseXYPlot):
    """ Plots a polygon in dataspace.

    Assuming that the index and value mappers are linear mappers, and that
    "index" corresponds to X-coordinates and "value" corresponds to
    Y-coordinates, the points are arranged in a counter-clockwise fashion.
    The polygon is closed automatically, so there is no need to reproduce
    the first point as the last point.

    Nonlinear mappers are possible, but the results may be unexpected. Only the
    data-space points are mapped in a nonlinear fashion. Straight lines
    connecting them in a linear screen-space become curved in a nonlinear
    screen-space; however, the drawing still contains straight lines in
    screen-space.

    If you don't want the edge of the polygon to be drawn, set **edge_color**
    to transparent; don't try to do this by setting **edge_width** to 0. In 
    some drawing systems, such as PostScript, a line width of 0 means to make
    the line as small as possible while still putting ink on the page. 
    """

    # The color of the line on the edge of the polygon.
    edge_color = black_color_trait

    # The thickness of the edge of the polygon.
    edge_width = Float(1.0)

    # The line dash style for the edge of the polygon.
    edge_style = LineStyle

    # The color of the face of the polygon.
    face_color = transparent_color_trait


    #### Private 'BaseXYPlot' interface ########################################

    def _gather_points(self):
        """ Collects the data points that are within the bounds of the plot and
        caches them.
        """
        if self._cache_valid:
            return

        index = self.index.get_data()
        value = self.value.get_data()

        if not self.index or not self.value:
            return

        if len(index) == 0 or len(value) == 0 or len(index) != len(value):
            logger.warn("Chaco2: using empty dataset; index_len=%d, value_len=%d." \
                                % (len(index), len(value)))
            self._cached_data_pts = []
            self._cache_valid = True
            return

        points = np.transpose(np.array((index,value)))
        self._cached_data_pts = points

        self._cache_valid = True


    def _render(self, gc, points):
        """ Renders an Nx2 array of screen-space points as a polygon.
        """
        gc.save_state()

        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_stroke_color(self.edge_color_)
        gc.set_line_width(self.edge_width)
        gc.set_line_dash(self.edge_style_)
        gc.set_fill_color(self.face_color_)

        gc.lines(points)
        gc.close_path()
        gc.draw_path()

        gc.restore_state()


    def _render_icon(self, gc, x, y, width, height):
        """ Renders a representation of this plot as an icon into the box
        defined by the parameters.

        Used by the legend.
        """
        gc.save_state()
        gc.set_stroke_color(self.edge_color_)
        gc.set_line_width(self.line_width)
        gc.set_line_dash(self.line_style_)
        gc.draw_rect((x,y,width,height))
        gc.restore_state()
        return


#### EOF #######################################################################
