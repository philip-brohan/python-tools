# Plain plot of orography field

import iris
import os
import numpy
import matplotlib.pyplot

# Load the orography cube
orog=iris.load_cube("%s/orography/elev.0.25-deg.nc" %
                    os.environ['SCRATCH'])
# Get rid of the spurious time dimension
orog=orog.collapsed('time',iris.analysis.MAX)
# Set all the land areas (height>=0) to 1
orog.data[numpy.where(orog.data>=0)]=1
# Set all the sea aread (height<0) to missing
orog.data[numpy.where(orog.data<0)]=numpy.NaN

# Now make the plot
fig=matplotlib.pyplot.figure()

# A4 size
fig.set_size_inches(11, 8)

# Plot the orography as an image
img=matplotlib.pyplot.imshow(orog.data,interpolation='bilinear')

# Don't want axes - turn them off
matplotlib.pyplot.axis('off')
img.axes.get_xaxis().set_visible(False)
img.axes.get_yaxis().set_visible(False)

# Output as pdf
matplotlib.pyplot.savefig('plot_orography.pdf', bbox_inches='tight', pad_inches = 0)
