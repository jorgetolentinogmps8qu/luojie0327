""" Makes a copy of the plot in the overlay and adds it to the canvas.
"""


# Enthought library imports
from enthought.traits.api import Bool, Callable, Enum, Float, Instance, Trait, Tuple
from enthought.enable2.api import Canvas, Component, Container

# Chaco imports
from enthought.chaco2.api import AbstractOverlay
from enthought.enable2.tools.api import DragTool


class PlotCloneTool(AbstractOverlay, DragTool):
    """ On a drag operation, draws an overlay of self.component underneath
    the cursor.  On drag_end, a copy of the plot is dropped onto the
    self.dest container.
    """

    # The container to add the cloned plot to
    dest = Instance(Container)

    # A function that gets called on drag_end.  It gets passed this tool
    # and the position at which to place the new cloned plot.
    plot_cloner = Callable

    # The amount to fade the plot when we draw as overlay
    alpha = Float(0.5)

    # The possible event states for this tool.
    event_state = Enum("normal", "dragging")

    capture_mouse = True

    # The (x,y) position of the "last" mouse position we received
    _offset = Trait(None, None, Tuple)

    # The relative position of the mouse_down_position to the origin
    # of the plot's coordinate system
    _offset_from_plot = Tuple

    # This is set to True before we attempt to move the plot, so that
    # we do not get called again, in case we are an overlay on the plot
    # we are drawing.
    _recursion_check = Bool(False)

    def overlay(self, component, gc, view_bounds=None, mode="normal"):
        if self._recursion_check:
            return
        else:
            if self._offset is not None and (self._offset[0] > 10 or
                    self._offset[1] > 10):
                gc.save_state()
                gc.clear_clip_path()
                gc.translate_ctm(*self._offset)
                gc.set_alpha(self.alpha)
                self._recursion_check = True
                self.component._draw(gc, view_bounds, mode)
                self._recursion_check = False
                gc.restore_state()

    def drag_start(self, event):
        """ Called when the drag operation starts.  
        
        Implements DragTool.
        """
        self._offset = (event.x - self.mouse_down_position[0],
                        event.y - self.mouse_down_position[1])
        self._offset_from_plot = (self.mouse_down_position[0] - self.component.x,
                                  self.mouse_down_position[1] - self.component.y)
        self.visible = True
        event.handled = True
    
    def dragging(self, event):
        self._offset = (event.x - self.mouse_down_position[0],
                        event.y - self.mouse_down_position[1])
        self.component.request_redraw()

    def drag_end(self, event):
        if self.plot_cloner is not None:
            # Recreate the event transform history and figure out the coordinates
            # of the event in the Canvas's coordinate system
            offset = self._offset_from_plot
            drop_position = (event.x - offset[0], event.y - offset[1])
            self.plot_cloner(self, drop_position)
        self._offset = None
        self.visible = False
        self.component.request_redraw()

