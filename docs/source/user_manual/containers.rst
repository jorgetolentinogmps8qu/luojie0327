
.. highlight:: python
   :linenothreshold: 10

*********************
Containers and Layout
*********************

Overview
========

It is quite common to need to display data side by side. In order to arrange
multiple plots and other components (e.g., colorbars) in a single panel,
Chaco uses *containers* to organize the layout.

 * Rendering order
 * Event dispatch
 * Layout and sizing

Chaco containers
================

Chaco implements 4 different containers:
:ref:`hv-plot-container`,
:ref:`grid-plot-container`, and :ref:`overlay-plot-container`.

All containers are derived from the base class
:class:`~chaco.base_plot_container.​BasePlotContainer`, and share
a common interface:

* ``__init__(*components, **parameters)`` (constructor of the container object):
  The constructor of a plot container takes a sequence of
  components, which are added to the container itself,
  and a set of keyword arguments, which are used to initialize the
  parameters of the container. For example::

      container = HPlotContainer(scatter_plot, line_plot, spacing=100)

  creates a container with horizontal layout containing two plots
  (``scatter_plot`` and ``line_plot``), with a spacing of 100 pixels between
  them.

* ``add(*components)``: Append ore or more plots to the ones already present in the
  container. For example, this is equivalent to the code above::

      container = HPlotContainer(spacing=100)
      container.add(line_plot, scatter_plot)

* ``remove(self, *components)``: Remove a sequence of components from the
  container

* ``insert(index, component)``: Inserts a component at a specific position
  in the components list

.. note::

    **Each plot can have only one container**, so adding the same plot to
    a second container will remove it from the first one. In the same way,
    adding the same plot multiple times will not have create multiple
    copies. Instead, one should create multiple plots objects.

    E.g., this code::

            # Create a vertical container containing two horizontal containers
            h_container1 = HPlotContainer()
            h_container2 = HPlotContainer()
            outer_container = VPlotContainer(h_container1, h_container2,
                                             stack_order="top_to_bottom")

            # Add the two plots to the first container
            h_container1.add(scatter_plot, line_plot1, line_plot2)

            # Now add the first line plot to the second container => it is removed
            # from the first, as each plot can only have one container
            h_container2.add(line_plot1)

    results in this layout:

      .. image:: images/user_guide/one_container_per_plot.png
          :height: 200pt



.. _hv-plot-container:

HPlotContainer and VPlotContainer
---------------------------------

:class:`~chaco.plot_containers.HPlotContainer` and
:class:`~chaco.plot_containers.VPlotContainer` display a set of components
in an horizontal and vertical stack, respectively, as shown in these simple
examples:

.. image:: images/hplotcontainer.png
    :height: 200pt

.. image:: images/vplotcontainer.png
    :height: 200pt

In both cases, a series of line plots and scatter plots is added to an
:class:`~chaco.plot_containers.HPlotContainer` or a
:class:`~chaco.plot_containers.VPlotContainer`::

        # Create the data and the PlotData object
        x = linspace(-14, 14, 100)
        y = sin(x) * x**3
        plotdata = ArrayPlotData(x = x, y = y)

        # Create a scatter plot
        scatter_plot = Plot(plotdata)
        scatter_plot.plot(("x", "y"), type="scatter", color="blue")

        # Create a line plot
        line_plot = Plot(plotdata)
        line_plot.plot(("x", "y"), type="line", color="blue")

        # Create a horizontal container and put the two plots inside it
        container = HPlotContainer(line_plot, scatter_plot)
        self.plot = container


:class:`~chaco.plot_containers.HPlotContainer` is also used often to
display a colorbar or legend to the side of a plot. For example, this
plot

.. image:: images/user_guide/h_container_colorbar.png
  :height: 200pt

was created using a color-mapped scatter plot and a colorbar inside a
horizontal container::

        # Create the plot
        plot = Plot(data)
        plot.plot(("index", "value", "color"), type="cmap_scatter",
                  color_mapper=jet)

        # Create the colorbar, handing in the appropriate range and colormap
        colormap = plot.color_mapper
        colorbar = ColorBar(index_mapper=LinearMapper(range=colormap.range),
                            color_mapper=colormap,
                            orientation='v',
                            resizable='v',
                            width=30,
                            padding=20)

        colorbar.padding_top = plot.padding_top
        colorbar.padding_bottom = plot.padding_bottom

        # Create a container to position the plot and the colorbar side-by-side
        container = HPlotContainer(plot, colorbar)


HPlotContainer parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

This is a list of parameters that are specific to
:class:`~chaco.plot_containers.HPlotContainer`

* ``stack_order``:
  Components added to the container are laid out left-to-right by default.
  This parameters control this behavior: ::

      stack_order = Enum("left_to_right", "right_to_left")

* ``spacing``:
  The amount of space to put between components.::

      spacing = Float(0.0)

* ``valign``:
  The vertical alignment of objects that don't span the full height.

      valign = Enum("bottom", "top", "center")


VPlotContainer parameters
^^^^^^^^^^^^^^^^^^^^^^^^^

This is a list of parameters that are specific to
:class:`~chaco.plot_containers.VPlotContainer`

* ``stack_order``:
  The order in which components in the plot container are laid out. The
  default behavior is bottom-to-top. ::

      stack_order = Enum("bottom_to_top", "top_to_bottom")

* ``spacing``:
  The amount of space to put between components.::

      spacing = Float(0.0)

* ``halign``:
  The horizontal alignment of objects that don't span the full width.::

    halign = Enum("left", "right", "center")


.. seealso::

    **HPlotContainer and VPlotContainer in action.** See ``demo/financial_plot.py``,
    ``demo/two_plots.py``, ``demo/advanced/scalar_image_function_inspector.py``,
    and ``demo/basc/cmap_scatter.py``
    in the Chaco examples directory.


.. _grid-plot-container:

GridPlotContainer
-----------------

Just as the name suggests, a :class:`~chaco.plot_containers.GridPlotContainer`
lays out plots in a regular grid.

Unlike the previous containers, one has to specify in advance the number
of rows and columns in the plot. Plots with different sizes and/or
aspect ratios are aligned according to the parameters ``halign`` and
``valign``.

For example, to generate this plot

.. image:: images/user_guide/grid_container.png
  :height: 250pt

one needs to create six plots of fixed height and add them successively
(left-to-right, top-to-bottom) to the
:class:`~chaco.plot_containers.GridPlotContainer`. Plots are aligned to
the top by setting ``valign = 'top'``.

The complete code looks like this:

::

    class GridContainerExample(HasTraits):

        plot = Instance(GridPlotContainer)

        traits_view = View(
            Item('plot', editor=ComponentEditor(), show_label=False),
            width=1000, height=600, resizable=True
        )

        def _plot_default(self):
            # Create a GridContainer to hold all of our plots: 2 rows, 3 columns
            container = GridPlotContainer(shape=(2,3),
                                          spacing=(10,5),
                                          valign='top',
                                          bgcolor='lightgray')

            # Create x data
            x = linspace(-5, 15.0, 100)
            pd = ArrayPlotData(index = x)

            # Plot some Bessel functions and add the plots to our container
            for i in range(6):
                data_name = 'y{}'.format(i)
                pd.set_data(data_name, jn(i,x))

                plot = Plot(pd)
                plot.plot(('index', data_name),
                          color=COLOR_PALETTE[i],
                          line_width=3.0)

                # Set each plot's aspect based on its position in the grid
                plot.set(height=((i % 3) + 1)*50,
                         resizable='h')

                # Add to the grid container
                container.add(plot)

            return container


GridPlotContainer parameters
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This is a list of parameters that are specific to
:class:`~chaco.plot_containers.GridPlotContainer`

* ``valign``:
  The vertical alignment of objects that don't span the full height.::

    valign = Enum("bottom", "top", "center")


* ``halign``:
  The horizontal alignment of objects that don't span the full width.::

    halign = Enum("left", "right", "center")

* ``spacing``: A tuple or list of ``(h_spacing, v_spacing)``,
  giving spacing values
  for the horizontal and vertical direction. Default is (0, 0).


.. seealso::

    **GridPlotContainer in action.** See ``demo/basic/grid_container.py``
    and ``demo/basic/grid_container_aspect_ratio.py``
    in the Chaco examples directory.

.. _overlay-plot-container:

OverlayPlotContainer
--------------------

Overlay containers :class:`~chaco.plot_containers.OverlayPlotContainer`
lay out plots on top of each other.
The :class:`chaco.plot.Plot` class
in Chaco is a special subclass of
:class:`~chaco.plot_containers.OverlayPlotContainer`.

Overlay containers can be used to create "inset" plots. In the following
code, for instance, we create a zoomable plot with an fixed inset showing the
full data: ::

    class OverlayContainerExample(HasTraits):

        plot = Instance(OverlayPlotContainer)

        traits_view = View(
            Item('plot', editor=ComponentEditor(), show_label=False),
            width=800, height=600, resizable=True
        )

        def _plot_default(self):
            # Create data
            x = linspace(-5, 15.0, 100)
            y = jn(3, x)
            pd = ArrayPlotData(index=x, value=y)

            zoomable_plot = Plot(pd)
            zoomable_plot.plot(('index', 'value'),
                               name='external', color='red', line_width=3)

            # Attach tools to the plot
            zoom = ZoomTool(component=zoomable_plot,
                            tool_mode="box", always_on=False)
            zoomable_plot.overlays.append(zoom)
            zoomable_plot.tools.append(PanTool(zoomable_plot))

            # Create a second inset plot, not resizable, not zoom-able
            inset_plot = Plot(pd)
            inset_plot.plot(('index', 'value'), color='blue')
            inset_plot.set(resizable = '',
                           bounds = [250, 150],
                           position = [450, 350],
                           border_visible = True
                           )

            # Create a container and add our plots
            container = OverlayPlotContainer()
            container.add(zoomable_plot)
            container.add(inset_plot)
            return container

The code above generates this plot:

.. image:: images/user_guide/overlay_container_inset.png
  :height: 250pt

.. seealso::

    **GridPlotContainer in action.** See ``demo/basic/inset_plot.py``
    and
    ``demo/advanced/scalar_image_function_inspector.py``
    in the Chaco examples directory. To learn more about sharing
    axes on overlapping plots, see ``demo/multiaxis.py`` and
    ``demo/multiaxis_with_Plot.py``.
