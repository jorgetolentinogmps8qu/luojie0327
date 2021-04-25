"""
Defines the PolarMapper class, which maps from a 1D region in data space
into a 1D output space.
"""

# Major library imports
from numpy import array

# Enthought library imports
from enthought.traits.api import Event, false, Float, HasTraits

# Local relative imports
from data_range_1d import DataRange1D
from abstract_mapper import AbstractMapper

###############################################################
# same as linear mapper at the moment... to be modified later #
###############################################################
class PolarMapper(AbstractMapper):
    """
    Maps a 1D data space to and from screen space by specifying a range in
    data space and a corresponding fixed line in screen space.
    
    This only concerns itself with metric and not with orientation, so to
    "flip" the screen space orientation, simply swap the values for low_pos
    and high_pos.
    """
    #------------------------------------------------------------------------
    # Private traits
    #------------------------------------------------------------------------
    
    
    _scale = Float(1.0)   # number of screen space units per data space unit
    _null_screen_range = false
    _null_data_range = false
    
    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def map_screen(self, data_array):
        """ map_screen(data_array) -> screen_array
        
        Converts radius and theta values from data_array 
        to x and y values and then maps 
        values from data space into screen space
        """
        self._compute_scale()
        if self._null_data_range:
            return array([self.low_pos] * len(data_array))
        else:
            return (data_array - self.range.low) * self._scale + self.low_pos

    def map_data(self, screen_val):
        """ map_data(screen_val) -> data_val

        Maps values from screen space into data space
        """
        self._compute_scale()
        if self._null_screen_range:
            return array([self.range.low])
        else:
            return (screen_val - self.low_pos) / self._scale + self.range.low
    
    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _compute_scale(self):
        if self._cache_valid:
            return
        
        if self.range is None:
            self._cache_valid = False
            return
        
        d = self.range
        screen_range = self.high_pos - self.low_pos 
        data_range = self._pol_to_rect(d.high) - self._pol_to_rect(d.low)
        if screen_range == 0.0:
            self._null_screen_range = True
        else:
            self._null_screen_range = False
        if data_range == 0.0:
            self._null_data_range = True
        else:
            self._scale = screen_range / data_range
            self._null_data_range = False
        
        self._cache_valid = True
        return
    
        
# EOF
