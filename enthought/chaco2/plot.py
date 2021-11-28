""" Defines the Plot class.
"""
# Major library imports
import itertools
import warnings
from numpy import arange, array, ndarray, linspace, transpose
from types import FunctionType

# Enthought library imports
from enthought.traits.api import Delegate, Dict, Instance, Int, List, Property, Str

# Local, relative imports
from abstract_colormap import AbstractColormap
from abstract_data_source import AbstractDataSource
from abstract_plot_data import AbstractPlotData
from array_data_source import ArrayDataSource
from array_plot_data import ArrayPlotData
from axis import PlotAxis
from base_xy_plot import BaseXYPlot
from colormapped_scatterplot import ColormappedScatterPlot
from contour_line_plot import ContourLinePlot
from contour_poly_plot import ContourPolyPlot
from cmap_image_plot import CMapImagePlot
from data_range_1d import DataRange1D
from data_range_2d import DataRange2D
from data_view import DataView
from grid import PlotGrid
from grid_data_source import GridDataSource
from grid_mapper import GridMapper
from image_data import ImageData
from image_plot import ImagePlot
from legend import Legend
from lineplot import LinePlot
from linear_mapper import LinearMapper
from log_mapper import LogMapper
from plot_containers import OverlayPlotContainer
from plot_label import PlotLabel
from polygon_plot import PolygonPlot
from scatterplot import ScatterPlot




#-----------------------------------------------------------------------------
# The Plot class
#-----------------------------------------------------------------------------

class Plot(DataView):
    """ Represents a correlated set of data, renderers, and axes in a single
    screen region.

    A Plot can reference an arbitrary amount of data and can have an
    unlimited number of renderers on it, but it has a single X-axis and a
    single Y-axis for all of its associated data. Therefore, there is a single
    range in X and Y, although there can be many different data series. A Plot
    also has a single set of grids and a single background layer for all of its
    renderers.  It cannot be split horizontally or vertically; to do so,
    create a VPlotContainer or HPlotContainer and put the Plots inside those.
    Plots can be overlaid as well; be sure to set the **bgcolor** of the
    overlaying plots to "none" or "transparent".

    A Plot consists of composable sub-plots.  Each of these is created
    or destroyed using the plot() or delplot() methods.  Every time that
    new data is used to drive these sub-plots, it is added to the Plot's
    list of data and data sources.  Data sources are reused whenever
    possible; in order to have the same actual array drive two de-coupled
    data sources, create those data sources before handing them to the Plot.
    """

    #------------------------------------------------------------------------
    # Data-related traits
    #------------------------------------------------------------------------

    # The PlotData instance that drives this plot.
    data = Instance(AbstractPlotData)

    # Mapping of data names from self.data to their respective datasources.
    datasources = Dict(Str, Instance(AbstractDataSource))

    #------------------------------------------------------------------------
    # General plotting traits
    #------------------------------------------------------------------------

    # Mapping of plot names to *lists* of plot renderers.
    plots = Dict(Str, List)

    # The default index to use when adding new subplots.
    default_index = Instance(AbstractDataSource)

    # Optional mapper for the color axis.  Not instantiated until first use;
    # destroyed if no color plots are on the plot.
    color_mapper = Instance(AbstractColormap)

    # List of colors to cycle through when auto-coloring is requested
    auto_colors = List(["gold", "brown", "lightblue", "darkblue", "purple"])

    # index into auto_colors list
    _auto_color_idx = Int

    #------------------------------------------------------------------------
    # Annotations and decorations
    #------------------------------------------------------------------------

    # The title of the plot.
    title = Property

    # The font to use for the title.
    title_font = Str("swiss 16")

    # Convenience attribute for title.overlay_position; can be "top",
    # "bottom", "left", or "right".
    title_position = Property

    # Use delegates to expose the other PlotLabel attributes of the plot title
    title_text = Delegate("_title", prefix="text", modify=True)
    title_color = Delegate("_title", prefix="color", modify=True)
    title_angle = Delegate("_title", prefix="angle", modify=True)

    # The PlotLabel object that contains the title.
    _title = Instance(PlotLabel)
    
    # The legend on the plot.
    legend = Instance(Legend)

    # Convenience attribute for legend.align; can be "ur", "ul", "ll", "lr".
    legend_alignment = Property

    #------------------------------------------------------------------------
    # Public methods
    #------------------------------------------------------------------------

    def __init__(self, data=None, **kwtraits):
        super(Plot, self).__init__(**kwtraits)
        if data is not None:
            if isinstance(data, AbstractPlotData):
                self.data = data
            elif type(data) in (ndarray, tuple, list):
                self.data = ArrayPlotData(data)
            else:
                raise ValueError, "Don't know how to create PlotData for data" \
                                  "of type " + str(type(data))

        if not self._title:
            self._title = PlotLabel(font=self.title_font, visible=False,
                                   overlay_position="top", component=self)

        if not self.legend:
            self.legend = Legend(visible=False, align="ur", error_icon="blank",
                                 padding=10, component=self)
        return

    def plot(self, data, type="line", name=None, index_scale="linear",
             value_scale="linear", **styles):
        """ Adds a new sub-plot using the given data and plot style.

        Parameters
        ==========
        data : string, tuple(string), list(string)
            The data to be plotted. The type of plot and the number of
            arguments determines how the arguments are interpreted:

            one item: (line/scatter)
                The data is treated as the value and self.default_index is
                used as the index.  If **default_index** does not exist, one is
                created from arange(len(*data*))
            two or more items: (line/scatter)
                Interpreted as (index, value1, value2, ...).  Each index,value
                pair forms a new plot of the type specified.
            two items: (cmap_scatter)
                Interpreted as (value, color_values).  Uses **default_index**.
            three or more items: (cmap_scatter)
                Interpreted as (index, val1, color_val1, val2, color_val2, ...)

        type : comma-delimited string of "line", "scatter", "cmap_scatter"
            The types of plots to add.
        name : string
            The name of the plot.  If None, then a default one is created
            (usually "plotNNN").
        index_scale : string
            The type of scale to use for the index axis. If not "linear", then
            a log scale is used.
        value_scale : string
            The type of scale to use for the value axis. If not "linear", then
            a log scale is used.
        styles : series of keyword arguments
            attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.

        Examples
        ========
        ::

            plot("my_data", type="line", name="myplot", color=lightblue)

            plot(("x-data", "y-data"), type="scatter")

            plot(("x", "y1", "y2", "y3"))

        Returns
        =======
        [str] -> list of names of the new plots created
        """

        if len(data) == 0:
            return

        if isinstance(data, basestring):
            data = (data,)

        self.index_scale = index_scale
        self.value_scale = value_scale

        # TODO: support lists of plot types
        plot_type = type
        if name is None:
            name = self._make_new_plot_name()
        plot_name = name
        if plot_type in ("line", "scatter", "polygon"):
            if len(data) == 1:
                if self.default_index is None:
                    # Create the default index based on the length of the first
                    # data series
                    value = self._get_or_create_datasource(data[0])
                    self.default_index = ArrayDataSource(arange(len(value.get_data())),
                                                         sort_order="none")
                    self.index_range.add(self.default_index)
                index = self.default_index
            else:
                index = self._get_or_create_datasource(data[0])
                if self.default_index is None:
                    self.default_index = index
                self.index_range.add(index)
                data = data[1:]

            new_plots = []
            for value_name in data:
                value = self._get_or_create_datasource(value_name)
                self.value_range.add(value)
                if plot_type == "line":
                    cls = LinePlot
                    # handle auto-coloring request
                    if styles.get("color") == "auto":
                        self._auto_color_idx = \
                            (self._auto_color_idx + 1) % len(self.auto_colors)
                        styles["color"] = self.auto_colors[self._auto_color_idx]
                elif plot_type == "scatter":
                    cls = ScatterPlot
                elif plot_type == "polygon":
                    cls = PolygonPlot
                else:
                    raise ValueError("Unhandled plot type: " + plot_type)

                if self.index_scale == "linear":
                    imap = LinearMapper(range=self.index_range)
                else:
                    imap = LogMapper(range=self.index_range)
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=self.value_range)
                else:
                    vmap = LogMapper(range=self.value_range)

                plot = cls(index=index,
                           value=value,
                           index_mapper=imap,
                           value_mapper=vmap,
                           orientation=self.orientation,
                           **styles)
                self.add(plot)
                new_plots.append(plot)

            self.plots[name] = new_plots
        elif plot_type == "cmap_scatter":
            if len(data) != 3:
                raise ValueError("Colormapped scatter plots require (index, value, color) data")
            else:
                index = self._get_or_create_datasource(data[0])
                if self.default_index is None:
                    self.default_index = index
                self.index_range.add(index)
                value = self._get_or_create_datasource(data[1])
                self.value_range.add(value)
                color = self._get_or_create_datasource(data[2])
                if not styles.has_key("color_mapper"):
                    raise ValueError("Scalar 2D data requires a color_mapper.")
                elif isinstance(styles["color_mapper"], AbstractColormap):
                    self.color_mapper = styles["color_mapper"]
                else:
                    self.color_mapper = styles["color_mapper"](DataRange1D(color))
                if self.index_scale == "linear":
                    imap = LinearMapper(range=self.index_range)
                else:
                    imap = LogMapper(range=self.index_range)
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=self.value_range)
                else:
                    vmap = LogMapper(range=self.value_range)

                styles.pop("color_mapper")
                cls = ColormappedScatterPlot
                plot = cls(index=index,
                           index_mapper=imap,
                           value=value,
                           value_mapper=vmap,
                           color_data=color,
                           color_mapper=self.color_mapper,
                           orientation=self.orientation,
                           **styles)
                self.add(plot)

            self.plots[name] = [plot]
        else:
            raise ValueError("Unknown plot type: " + plot_type)

        return self.plots[name]


    def img_plot(self, data, name=None, colormap=None,
                 xbounds=None, ybounds=None, **styles):
        """ Adds image plots to this Plot object.

        If *data* has shape (N, M, 3) or (N, M, 4), then it is treated as RGB or
        RGBA (respectively) and *colormap* is ignored.

        If *data* is an array of floating-point data, and no colormap is provided,
        then a ValueError is thrown.

        *Data* should be in row-major order, so that xbounds corresponds to
        *data*'s second axis, and ybounds corresponds to the first axis.

        Parameters
        ==========
        data : string
            The name of the data array in self.plot_data
        name : string
            The name of the plot; if omitted, then a name is generated.
        xbounds, ybounds : tuples of (low, high)
            Bounds in data space where this image resides.
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()

        value = self._get_or_create_datasource(data)
        array_data = value.get_data()
        if len(array_data.shape) == 3:
            if array_data.shape[2] not in (3,4):
                raise ValueError("Image plots require color depth of 3 or 4.")
            cls = ImagePlot
            kwargs = dict(**styles)
        else:
            if colormap is None:
                if self.color_mapper is None:
                    raise ValueError("Scalar 2D data requires a colormap.")
                else:
                    colormap = self.color_mapper
            elif isinstance(colormap, AbstractColormap):
                if colormap.range is None:
                    colormap.range = DataRange1D(value)
            else:
                colormap = colormap(DataRange1D(value))
            self.color_mapper = colormap
            cls = CMapImagePlot
            kwargs = dict(value_mapper=colormap, **styles)

        # process xbounds to get a linspace
        if isinstance(xbounds, basestring):
            xbounds = self._get_or_create_datasource(xbounds).get_data()
        if xbounds is None:
            xs = arange(array_data.shape[1])
        elif isinstance(xbounds, tuple):
            xs = linspace(xbounds[0], xbounds[1], array_data.shape[1])
        elif isinstance(xbounds, ndarray):
            if len(xbounds.shape) == 1 and len(xbounds) == array_data.shape[1]:
                xs = linspace(xbounds[0], xbounds[-1], array_data.shape[1])
            elif xbounds.shape == array_data.shape:
                xs = xbounds[0,:]
            else:
                raise ValueError("xbounds shape not commensurate with data")
        else:
            raise ValueError("xbounds must be None, a tuple, an array, or a PlotData name")

        # process xbounds to get a linspace
        if isinstance(ybounds, basestring):
            ybounds = self._get_or_create_datasource(ybounds).get_data()
        if ybounds is None:
            ys = arange(array_data.shape[0])
        elif isinstance(ybounds, tuple):
            ys = linspace(ybounds[0], ybounds[1], array_data.shape[0])
        elif isinstance(ybounds, ndarray):
            if len(ybounds.shape) == 1 and len(ybounds) == array_data.shape[0]:
                ys = linspace(ybounds[0], ybounds[-1], array_data.shape[0])
            elif ybounds.shape == array_data.shape:
                ys = ybounds[:,0]
            else:
                raise ValueError("ybounds shape not commensurate with data")
        else:
            raise ValueError("ybounds must be None, a tuple, an array, or a PlotData name")

        # Create the index and add its datasources to the appropriate ranges
        index = GridDataSource(xs, ys, sort_order=('ascending', 'ascending'))
        self.range2d.add(index)
        mapper = GridMapper(range=self.range2d)

        plot = cls(index=index, value=value, index_mapper=mapper, **kwargs)

        # image plots have an origin at the top
        plot.y_direction = "flipped"
        self.y_direction = "flipped"
        self.x_axis.orientation = "top"

        # turn grids off by default on image plots
        self.x_grid.visible = False
        self.y_grid.visible = False

        self.add(plot)
        self.plots[name] = [plot]
        return self.plots[name]


    def contour_plot(self, data, type="line", name=None, poly_cmap=None,
                     xbounds=None, ybounds=None, **styles):
        """ Adds contour plots to this Plot object.

        Parameters
        ==========
        data : string
            The name of the data array in self.plot_data, which must be
            floating point data.
        type : comma-delimited string of "line", "poly"
            The type of contour plot to add. If the value is "poly"
            and no colormap is provided, then a ValueError is thrown.
        name : string
            The name of the plot; if omitted, then a name is generated.
        poly_cmap : string
            The name of the color-map function to call (in
            chaco2.default_colormaps) or an AbstractColormap instance
            to use for contour poly plots (ignored for contour line plots)
        xbounds, ybounds : tuples of (low, high) in data space
            Bounds where this image resides.
        styles : series of keyword arguments
            Attributes and values that apply to one or more of the
            plot types requested, e.g.,'line_color' or 'line_width'.
        """
        if name is None:
            name = self._make_new_plot_name()

        value = self._get_or_create_datasource(data)
        array_data = value.get_data()
        if value.value_depth != 1:
            raise ValueError("Contour plots require 2D scalar field")
        if type == "line":
            cls = ContourLinePlot
            kwargs = dict(**styles)
            # if colors is given as a factory func, use it to make a
            # concrete colormapper. Better way to do this?
            if "colors" in kwargs:
                cmap = kwargs["colors"]
                if isinstance(cmap, FunctionType):
                    kwargs["colors"] = cmap(DataRange1D(value))
        elif type == "poly":
            if poly_cmap is None:
                raise ValueError("Scalar 2D data requires a colormap.")
            elif isinstance(poly_cmap, AbstractColormap):
                pass
            else:
                poly_cmap = poly_cmap(DataRange1D(value))
            cls = ContourPolyPlot
            kwargs = dict(color_mapper=poly_cmap, **styles)
        else:
            raise ValueError("Unhandled contour plot type: " + type)

        # process xbounds to get a linspace
        if isinstance(xbounds, basestring):
            xbounds = self._get_or_create_datasource(xbounds).get_data()
        if xbounds is None:
            xs = arange(array_data.shape[1])
        elif isinstance(xbounds, tuple):
            xs = linspace(xbounds[0], xbounds[1], array_data.shape[1])
        elif isinstance(xbounds, ndarray):
            if len(xbounds.shape) == 1 and len(xbounds) == array_data.shape[1]:
                xs = linspace(xbounds[0], xbounds[-1], array_data.shape[1])
            elif xbounds.shape == array_data.shape:
                xs = linspace(xbounds[0,0],xbounds[0,-1],array_data.shape[1])
            else:
                raise ValueError("xbounds shape not commensurate with data")
        else:
            raise ValueError("xbounds must be None, a tuple, an array, or a PlotData name")

        # process xbounds to get a linspace
        if isinstance(ybounds, basestring):
            ybounds = self._get_or_create_datasource(ybounds).get_data()
        if ybounds is None:
            ys = arange(array_data.shape[0])
        elif isinstance(ybounds, tuple):
            ys = linspace(ybounds[0], ybounds[1], array_data.shape[0])
        elif isinstance(ybounds, ndarray):
            if len(ybounds.shape) == 1 and len(ybounds) == array_data.shape[0]:
                ys = linspace(ybounds[0], ybounds[-1], array_data.shape[0])
            elif ybounds.shape == array_data.shape:
                ys = linspace(ybounds[0,0],ybounds[-1,0],array_data.shape[0])
            else:
                raise ValueError("ybounds shape not commensurate with data")
        else:
            raise ValueError("ybounds must be None, a tuple, an array, or a PlotData name")

        # Create the index and add its datasources to the appropriate ranges
        index = GridDataSource(xs, ys, sort_order=('ascending', 'ascending'))
        self.range2d.add(index)
        mapper = GridMapper(range=self.range2d)

        plot = cls(index=index, value=value, index_mapper=mapper, **kwargs)
        plot.y_direction = "flipped"
        self.y_direction = "flipped"
        self.x_axis.orientation = "top"

        # turn grids off by default on contour plots
        self.x_grid.visible = False
        self.y_grid.visible = False

        self.add(plot)
        self.plots[name] = [plot]
        return self.plots[name]



    def delplot(self, *names):
        """ Removes the named sub-plots. """

        # This process involves removing the plots, then checking the index range
        # and value range for leftover datasources, and removing those if necessary.

        # Remove all the renderers from us (container) and create a set of the
        # datasources that we might have to remove from the ranges
        deleted_sources = set()
        for renderer in itertools.chain(*[self.plots.pop(name) for name in names]):
            self.remove(renderer)
            deleted_sources.add(renderer.index)
            deleted_sources.add(renderer.value)

        # Cull the candidate list of sources to remove by checking the other plots
        sources_in_use = set()
        for p in itertools.chain(*self.plots.values()):
                sources_in_use.add(p.index)
                sources_in_use.add(p.value)

        unused_sources = deleted_sources - sources_in_use - set([None])

        # Remove the unused sources from all ranges
        for source in unused_sources:
            if source.index_dimension == "scalar":
                # Try both index and range, it doesn't hurt
                self.index_range.remove(source)
                self.value_range.remove(source)
            elif source.index_dimension == "image":
                self.range2d.remove(source)
            else:
                warnings.warn("Couldn't remove datasource from datarange.")

        return


    def map_screen(self, data_array):
        """ Maps an array of data points to screen space and returns an array
        of screen space points.
        """
        # data_array is Nx2 array
        if len(data_array) == 0:
            return []
        x_ary, y_ary = transpose(data_array)
        sx = self.index_mapper.map_screen(x_ary)
        sy = self.value_mapper.map_screen(y_ary)
        if self.orientation == "h":
            return transpose(array((sx,sy)))
        else:
            return transpose(array((sy,sx)))


    #------------------------------------------------------------------------
    # Private methods
    #------------------------------------------------------------------------



    def _make_new_plot_name(self):
        """ Returns a string that is not already used as a plot title.
        """
        n = len(self.plots)
        plot_template = "plot%d"
        while 1:
            name = plot_template % n
            if name not in self.plots:
                break
            else:
                n += 1
        return name

    def _get_or_create_datasource(self, name):
        """ Returns the data source associated with the given name, or creates
        it if it doesn't exist.
        """

        if name not in self.datasources:
            data = self.data.get_data(name)

            if type(data) in (list, tuple):
                data = array(data)

            if isinstance(data, ndarray):
                if len(data.shape) == 1:
                    ds = ArrayDataSource(data, sort_order="none")
                elif len(data.shape) == 2:
                    ds = ImageData(data=data, value_depth=1)
                elif len(data.shape) == 3:
                    if data.shape[2] in (3,4):
                        ds = ImageData(data=data, value_depth=data.shape[2])
                    else:
                        raise ValueError("Unhandled array shape in creating new plot: " \
                                         + str(data.shape))

            elif isinstance(data, AbstractDataSource):
                ds = data

            else:
                raise ValueError("Couldn't create datasource for data of type " + \
                                 str(type(data)))

            self.datasources[name] = ds

        return self.datasources[name]

    #------------------------------------------------------------------------
    # Event handlers
    #------------------------------------------------------------------------

    def _color_mapper_changed(self):
        for plist in self.plots.values():
            for plot in plist:
                plot.color_mapper = self.color_mapper
        self.invalidate_draw()

    def _data_changed(self, old, new):
        if old:
            old.on_trait_change(self._data_update_handler, "data_changed",
                                remove=True)
        if new:
            new.on_trait_change(self._data_update_handler, "data_changed")

    def _data_update_handler(self, name, event):
        # event should be a dict with keys "added", "removed", and "changed",
        # per the comments in AbstractPlotData.
        if event.has_key("added"):
            pass

        if event.has_key("removed"):
            pass

        if event.has_key("changed"):
            for name in event["changed"]:
                if self.datasources.has_key(name):
                    source = self.datasources[name]
                    source.set_data(self.data.get_data(name))

    def _plots_items_changed(self, event):
        if self.legend:
            self.legend.plots = self.plots

    def _index_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.index_scale == "linear":
            imap = LinearMapper(range=self.index_range,
                                screen_bounds=self.index_mapper.screen_bounds)
        else:
            imap = LogMapper(range=self.index_range,
                             screen_bounds=self.index_mapper.screen_bounds)
        self.index_mapper = imap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.index_scale == "linear":
                    imap = LinearMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds)
                else:
                    imap = LogMapper(range=plot.index_range,
                                screen_bounds=plot.index_mapper.screen_bounds)
                plot.index_mapper = imap

    def _value_scale_changed(self, old, new):
        if old is None: return
        if new == old: return
        if not self.range2d: return
        if self.value_scale == "linear":
            vmap = LinearMapper(range=self.value_range,
                                screen_bounds=self.value_mapper.screen_bounds)
        else:
            vmap = LogMapper(range=self.value_range,
                             screen_bounds=self.value_mapper.screen_bounds)
        self.value_mapper = vmap
        for key in self.plots:
            for plot in self.plots[key]:
                if not isinstance(plot, BaseXYPlot):
                    raise ValueError("log scale only supported on XY plots")
                if self.value_scale == "linear":
                    vmap = LinearMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds)
                else:
                    vmap = LogMapper(range=plot.value_range,
                                screen_bounds=plot.value_mapper.screen_bounds)
                plot.value_mapper = vmap

    def __title_changed(self, old, new):
        self._overlay_change_helper(old, new)

    def _title_font_changed(self, old, new):
        self._title.font = new

    def _legend_changed(self, old, new):
        self._overlay_change_helper(old, new)
        if new:
            new.plots = self.plots

    def _handle_range_changed(self, name, old, new):
        """ Overrides the DataView default behavior.

        Primarily changes how the list of renderers is looked up.
        """
        mapper = getattr(self, name+"_mapper")
        if mapper.range == old:
            mapper.range = new
        if old is not None:
            for datasource in old.sources[:]:
                old.remove(datasource)
                if new is not None:
                    new.add(datasource)
        range_name = name + "_range"
        for renderer in itertools.chain(*self.plots.values()):
            if hasattr(renderer, range_name):
                setattr(renderer, range_name, new)

    #------------------------------------------------------------------------
    # Property getters and setters
    #------------------------------------------------------------------------

    def _set_legend_alignment(self, align):
        if self.legend:
            self.legend.align = align

    def _get_legend_alignment(self):
        if self.legend:
            return self.legend.align
        else:
            return None

    def _set_title(self, text):
        self._title.text = text
        if text.strip() != "":
            self._title.visible = True
        else:
            self._title.visible = False

    def _get_title(self):
        return self._title.text

    def _set_title_position(self, pos):
        if self._title is not None:
            self.title.overlay_position = pos

    def _get_title_position(self):
        if self._title is not None:
            return self.title.overlay_position
        else:
            return None
