
from enthought.etsconfig.api import ETSConfig
from enthought.enable.tools.toolbars.toolbar_buttons import Button
from enthought.chaco.tools.simple_zoom import SimpleZoom
from enthought.chaco.plot_graphics_context import PlotGraphicsContext
from enthought.kiva.backend_image import Image
from enthought.pyface.image_resource import ImageResource
from enthought.pyface.api import FileDialog, OK, error
from enthought.traits.api import Instance, Str, Property, cached_property, \
    List, Int


class ToolbarButton(Button):
    image = Str()
    _image = Instance(Image)

    color = 'black'
    
    width = Property(Int, depends_on='label, image')
    height = Property(Int, depends_on='label, image')
    
    # bounds are used for hit testing
    bounds = Property(List, depends_on='label, image')

    def __init__(self, *args, **kw):
        super(ToolbarButton, self).__init__(*args, **kw)
        
        image_resource = ImageResource(self.image)
        self._image = Image(image_resource.absolute_path)

    @cached_property
    def _get_width(self):
        gc = PlotGraphicsContext((100,100), dpi=72)
        gc.set_font(self.label_font)
        (w, h, descent, leading) = gc.get_full_text_extent(self.label)
        return max(self._image.width(), w)
    
    @cached_property
    def _get_height(self):
        gc = PlotGraphicsContext((100,100), dpi=72)
        gc.set_font(self.label_font)
        (w, h, descent, leading) = gc.get_full_text_extent(self.label)
        return self._image.height() + h

    @cached_property
    def _get_bounds(self):
        return [self.width, self.height]
    
    def _draw_actual_button(self, gc):
        x_offset = self.x + (self.width - self._image.width())/2
        gc.draw_image(self._image,
                      (x_offset, self.y+2, self._image.width(), self._image.height()))
        
        if self.label is not None and len(self.label) > 0:
            gc.set_font(self.label_font)
            
            (w, h, descent, leading) = gc.get_full_text_extent(self.label)
            if w < self.width:
                x_offset = self.x + (self.width - w)/2
            else:
                x_offset = self.x
            
            gc.set_text_position(x_offset, self.y-8)
            gc.show_text(self.label)

class IndexAxisLogButton(ToolbarButton):
    label = 'X Log Scale'
    tooltip = 'Change index axis scale'
    image = 'zoom-fit-width'

    def perform(self, event):
        if self.container.component.index_scale == 'linear':
            self.container.component.index_scale = 'log'
        else:
            self.container.component.index_scale = 'linear'
        self.container.request_redraw()
        return

class ValueAxisLogButton(ToolbarButton):
    label = 'Y Log Scale'
    tooltip = 'Change value axis scale'
    image = 'zoom-fit-height'

    def perform(self, event):
        if self.container.component.value_scale == 'linear':
            self.container.component.value_scale = 'log'
        else:
            self.container.component.value_scale = 'linear'
        self.container.request_redraw()
        return

class ZoomResetButton(ToolbarButton):
    label = 'Zoom Reset'
    tooltip = 'Zoom Reset'
    image = 'zoom-original'

    def perform(self, event):
        plot_component = self.container.component

        for overlay in plot_component.overlays:
            if isinstance(overlay, SimpleZoom):
                overlay._reset_state_pressed()

        self.container.request_redraw()



class SaveAsButton(ToolbarButton):
    label = 'Save As'
    tooltip = 'Save As'
    image = 'document-save'

    def perform(self, event):
        
        plot_component = self.container.component

        filter = 'PNG file (*.png)|*.png|\nTIFF file (*.tiff)|*.tiff|'
        dialog = FileDialog(action='save as', wildcard=filter)

        if dialog.open() != OK:
            return

        # Remove the toolbar before saving the plot, so the output doesn't
        # include the toolbar.
        plot_component.remove_toolbar()

        filename = dialog.path

        width, height = plot_component.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)
        try:
            gc.save(filename)
        except KeyError, e:
            errmsg = "The filename must have an extension that matches a graphics"
            errmsg = errmsg + " format, such as '.png' or '.tiff'."
            if str(e.message) != '':
                errmsg = ("Unknown filename extension: '%s'\n" % str(e.message)) + errmsg
            
            error(None, errmsg, title="Invalid Filename Extension")

        # Restore the toolbar.
        plot_component.add_toolbar()



class CopyToClipboardButton(ToolbarButton):
    label = "Copy Image"
    tooltip = 'Copy to the clipboard'
    image = 'edit-copy'

    def perform(self, event):
        plot_component = self.container.component

        # Remove the toolbar before saving the plot, so the output doesn't
        # include the toolbar.
        plot_component.remove_toolbar()

        width, height = plot_component.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)

        if ETSConfig.toolkit == 'wx':
            self._perform_wx(width, height, gc)
        else:
            pass

        # Restore the toolbar.
        plot_component.add_toolbar()


    def _perform_wx(self, width, height, gc):
        import wx

        bitmap = wx.BitmapFromBufferRGBA(width+1, height+1, gc.bmp_array.flatten())
        data = wx.BitmapDataObject()
        data.SetBitmap(bitmap)
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error")

class ExportDataToClipboardButton(ToolbarButton):
    label = "Copy Data"
    tooltip = 'Copy data to the clipboard'
    image = 'application-vnd-ms-excel'

    def perform(self, event):
        plot_component = self.container.component

        # Remove the toolbar before saving the plot, so the output doesn't
        # include the toolbar.
        plot_component.remove_toolbar()

        width, height = plot_component.outer_bounds

        gc = PlotGraphicsContext((width, height), dpi=72)
        gc.render_component(plot_component)

        if ETSConfig.toolkit == 'wx':
            self._perform_wx(width, height, gc)
        else:
            pass

        # Restore the toolbar.
        plot_component.add_toolbar()

    def _get_data_from_plots(self):
        data = []
        for renderers in self.container.component.plots.values():
            for renderer in renderers:
                data.append(renderer.index.get_data())
                data.append(renderer.value.get_data())
        return data

    def _perform_wx(self, width, height, gc):
        import wx
        
        data = self._get_data_from_plots()
        data_str = ''
        for row in data:
            data_str += ','.join(['%f' % f for f in row.tolist()]) + '\n'
        data_obj = wx.TextDataObject(data_str)

        import pdb;pdb.set_trace()
        
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(data_obj)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Unable to open the clipboard.", "Error")


