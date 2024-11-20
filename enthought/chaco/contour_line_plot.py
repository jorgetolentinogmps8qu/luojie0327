""" Defines the ContourLinePlot class.
"""

# Major library imports
from numpy import array, meshgrid, transpose

# Enthought library imports
from enthought.enable.api import LineStyle
from enthought.traits.api import Bool, Dict, Float, List, Str, Trait

# Local relative imports
from base_contour_plot import BaseContourPlot
from color_mapper import ColorMapper
from contour.contour import Cntr


class ContourLinePlot(BaseContourPlot):
    """ Takes a value data object whose elements are scalars, and renders them
    as a contour plot.
    """

    # TODO: Modify ImageData to explicitly support scalar value arrays

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The thickness(es) of the contour lines.
    widths = Trait(1.0, Float, List)
    
    # The line dash style(s).
    styles = Trait("signed", Str, List)   

    # Line style for positive levels.
    positive_style = LineStyle("solid")

    # Line style for negative levels.
    negative_style = LineStyle("dash")

    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    # Are the cached contours valid? If False, new ones need to be computed.
    _contour_cache_valid = Bool(False)

    # Cached collection of traces.
    _cached_contours = Dict

    # Is the cached width data valid?
    _widths_cache_valid = Bool(False)

    # Is the cached style data valid?
    _styles_cache_valid = Bool(False)
    
    # Cached list of line widths
    _widths = List

    # Cached list of line styles
    _styles = List

    # Mapped trait used to convert user-suppied line style values to 
    # AGG-acceptable ones. (Mapped traits in lists are not supported, must be
    # converted one at a time.)
    _style_map_trait = LineStyle

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _render(self, gc):
        """ Actually draws the plot. 
        
        Implements the Base2DPlot interface.
        """
        if not self._level_cache_valid:
            self._update_levels()
        if not self._contour_cache_valid:
            self._update_contours()
        if not self._widths_cache_valid:
            self._update_widths()
        if not self._styles_cache_valid:
            self._update_styles()
        if not self._colors_cache_valid:
            self._update_colors()

        gc.save_state()
        gc.set_antialias(True)
        gc.clip_to_rect(self.x, self.y, self.width, self.height)
        gc.set_alpha(self.alpha)
        
        for i in range(len(self._levels)):
            gc.set_stroke_color(self._colors[i])
            gc.set_line_width(self._widths[i])
            gc.set_line_dash(self._styles[i])
            for trace in self._cached_contours[self._levels[i]]:
                if self.orientation == "h":
                    strace = self.index_mapper.map_screen(trace)
                else:
                    strace = array(self.index_mapper.map_screen(trace))[:,::-1]
                gc.begin_path()
                gc.lines(strace)
                gc.stroke_path()

        gc.restore_state()

    def _update_contours(self):
        """ Updates the cache of contour lines """
        # x and ydata are "fenceposts" so ignore the last value        
        # XXX: this truncaton is causing errors in Cntr() as of r13735
        if self.orientation == "h":
            xg, yg = meshgrid(self.index._xdata.get_data(), #[:-1],
                              self.index._ydata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value)
        else:
            yg, xg = meshgrid(self.index._ydata.get_data(), #[:-1],
                              self.index._xdata.get_data()) #[:-1])
            c = Cntr(xg, yg, self.value.raw_value.T)
        self._cached_contours = {}
        for level in self._levels:
            self._cached_contours[level] = []
            traces = c.trace(level)
            for trace in traces:
                self._cached_contours[level].append(transpose(trace))
        self._contour_cache_valid = True

    def _update_levels(self):
        """ Extends the parent method to also invalidate some other things """
        super(ContourLinePlot, self)._update_levels()
        self._contour_cache_valid = False
        self._widths_cache_valid = False
        self._styles_cache_valid = False

    def _update_widths(self):
        """ Updates the widths cache.
        """
        # If we are given a single width, apply it to all levels
        if isinstance(self.widths, float):
            self._widths = [self.widths] * len(self._levels)

        # If the list of widths is shorter than the list of levels, 
        # simply repeat widths from the beginning of the list as needed
        else:
            self._widths = []
            for i in range(len(self._levels)):
                self._widths.append(self.widths[i%len(self.widths)])

        self._widths_cache_valid = True

    def _update_styles(self):
        """ Updates the styles cache.
        """
        # If the style type is "signed" then assign styles to levels based
        # on their sign 
        if self.styles == "signed":
            self._styles = []
            for level in self._levels:
                if level < 0:
                    self._styles.append(self.negative_style_)
                else:
                    self._styles.append(self.positive_style_)

        # If we not given a list, apply the one style to all levels
        elif not isinstance(self.styles, list):
            self._style_map_trait = self.styles
            self._styles = [self._style_map_trait_] * len(self._levels)

        # If the list of styles is shorter than the list of levels, 
        # simply repeat styles from the beginning of the list as needed
        else:
            self._styles = []
            for i in range(len(self._levels)):
                self._style_map_trait = self.styles[i%len(self.styles)]      
                self._styles.append(self._style_map_trait_)

        self._styles_cache_valid = True


    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------
        
    def _widths_changed(self):
        if self._level_cache_valid: 
            self._update_widths()
            self.invalidate_draw()

    def _styles_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

    def _negative_style_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

    def _positive_style_changed(self):
        if self._level_cache_valid: 
            self._update_styles()
            self.invalidate_draw()

