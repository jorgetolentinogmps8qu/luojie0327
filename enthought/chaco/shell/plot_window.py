""" Defines the PlotWindow class.
"""
import wx

from enthought.enable.wx_backend.api import Window
from enthought.chaco.shell.scaly_plot import ScalyPlot


class PlotWindow(wx.Frame):
    """ A window for holding top-level plot containers.
    
    Contains many utility methods for controlling the appearance of the
    window, which mostly pass through to underlying WX calls.
    """

    def __init__(self, is_image=False, bgcolor="white", 
                 image_default_origin="top left", *args, **kw):

        kw.setdefault("size", (600,600))
        wx.Frame.__init__(self, None, *args, **kw )
        
        # Some defaults which should be overridden by preferences.
        self.bgcolor = bgcolor
        self.image_default_origin = image_default_origin

        # Create an empty top-level container
        if is_image:
            top_container = self._create_top_img_container()
        else:
            top_container = self._create_top_container()

        # The PlotSession of which we are a part.  We need to know this in order
        # to notify it of our being closed, etc.
        self.session = None


        # Create the Enable Window object, and store a reference to it.
        # (This will be handy later.)  The Window requires a WX parent object
        # as its first argument, so we just pass 'self'.
        self.plot_window = Window(self, component=top_container)
        
        # We'll create a default sizer to put our plot_window in.
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        # Since Window is an Enable object, we need to get its corresponding
        # WX control.  This is stored in its ".control" attribute.
        sizer.Add(self.plot_window.control, 1, wx.EXPAND)

        # Hook up event handlers for destroy, etc.
        wx.EVT_WINDOW_DESTROY(self, self._on_window_close)
        
        # More WX boilerplate.
        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        self.Show(True)
        return

    def get_container(self):
        return self.plot_window.component

    def set_container(self, container):
        self.plot_window.component = container
    
    def iconize(self, iconize):
        """Iconizes the window if *iconize* is True.
        """
        self.Iconize(iconize)
    
    def maximize(self, maximize):
        """ If *maximize* is True, maximizes the window size; restores if False.
        """
        self.Maximize(maximize)

    def set_size(self, width, height):
        self.SetSize((width, height))

    def set_title(self, title):
        self.SetTitle(title)

    def raise_window(self):
        """Raises this window to the top of the window hierarchy.
        """
        self.Raise()

    def close(self):
        self.Close()

    # This is a Python property because this is not a HasTraits subclass.
    container = property(get_container, set_container)

    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------

    def _create_top_container(self):
        plot = ScalyPlot(
            padding=50, 
            fill_padding=True,
            bgcolor=self.bgcolor,
            use_backbuffer=True,
        )
        return plot

    def _create_top_img_container(self):
        plot = ScalyPlot(
            padding=50,
            fill_padding=True,
            bgcolor=self.bgcolor,
            use_backbuffer=True,
            default_origin=self.image_default_origin,
        )
        return plot


    def _on_window_close(self, event):
        if self.session:
            try:
                ndx = self.session.windows.index(self)
                self.session.del_window(ndx)
            except ValueError:
                pass


# EOF
