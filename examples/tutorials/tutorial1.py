#!/usr/bin/env python
#
#
# Tutorial 1. Creating a plot and saving it as an image to disk.


# First, we create two arrays of data, x and y.  'x' will be a sequence of
# 100 points spanning the range -2pi to 2pi, and 'y' will be sin(x).
from scipy import arange, pi, sin
numpoints = 100
step = 4*pi / numpoints
x = arange(-2*pi, 2*pi+step/2, step)
y = sin(x)


# Now that we have our data, we can use a factory function to create the
# line plot for us.  Chaco provides a few factories to simplify creating common
# plot types (line, scatter, etc.).  In later tutorials we'll see what the
# factories are actually doing, and how to manually assemble plotting
# primitives in more powerful ways.  For now, factories suit our needs.
from enthought.chaco2 import api as chaco2
myplot = chaco2.create_line_plot((x,y), bgcolor="white", add_grid=True, add_axis=True)

# We now need to set the plot's size, and add a little padding for the axes.
# (Normally, when Chaco plots are placed inside WX windows, the bounds are
# set automatically by the window.)
myplot.padding = 50
myplot.bounds = [400,400]


# Now we create a canvas of the appropriate size and ask it to render
# our component.  (If we wanted to display this plot in a window, we
# would not need to create the graphics context ourselves; it would be
# created for us by the window.)
plot_gc = chaco2.PlotGraphicsContext(myplot.outer_bounds)
plot_gc.render_component(myplot)

# Get the directory to save the image in
import os, sys
print 'Please enter a path in which to place generated plots.'
print 'Press <ENTER> to generate in the current directory.'
path = raw_input('Path: ').strip()

if len(path) > 0 and not os.path.exists(path):
    print 'The given path does not exist.'
    sys.exit()
    
if len(path) == 0:
    answer = raw_input('Generate plots in the current directory? [Y/N]: ')
    if answer.lower() <> 'y':
        sys.exit()

# Finally, we tell the graphics context to save itself to disk as an image.
plot_gc.save(os.path.join(path, "tutorial1.png"))

