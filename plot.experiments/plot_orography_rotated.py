# Plain plot of orography field
#  With a rotated pole.

import iris
import os
import numpy
import matplotlib.pyplot

# Remove incomprehensible error message
iris.FUTURE.netcdf_promote=True

# Load the orography cube
orog=iris.load_cube("%s/orography/elev.0.25-deg.nc" %
                    os.environ['SCRATCH'])
# Get rid of the spurious time dimension
orog=orog.collapsed('time',iris.analysis.MAX)
# Set all the land areas (height>=0) to 1
orog.data[numpy.where(orog.data>=0)]=1
# Set all the sea aread (height<0) to missing
orog.data[numpy.where(orog.data<0)]=numpy.NaN
# Specif the coordinate dimensions
cs=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
orog.coord('latitude').coord_system=cs
orog.coord('longitude').coord_system=cs

# Make a dummy cube on a rotated grid
cs=iris.coord_systems.RotatedGeogCS(0,60)
lat_values=numpy.arange(90,-90,-0.35)
lon_values=numpy.arange(-100,260,0.25)
latitude = iris.coords.DimCoord(lat_values,
                                standard_name='latitude',
                                units='degrees_north',
                                coord_system=cs)
lon_values=numpy.arange(-90,270,0.25)
longitude = iris.coords.DimCoord(lon_values,
                                standard_name='longitude',
                                units='degrees_east',
                                coord_system=cs)
dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
rotated_cube = iris.cube.Cube(dummy_data, 
                              dim_coords_and_dims=[(latitude, 0),
                                                   (longitude, 1)])

# Regrid the orography onto the dummy cube
rotated_orog=orog.regrid(rotated_cube,iris.analysis.Linear())

# Now make the plot
fig=matplotlib.pyplot.figure()

# A4 size
fig.set_size_inches(11, 8)

# Plot the orography as an image
img=matplotlib.pyplot.imshow(rotated_orog.data,interpolation='bilinear')

# Don't want axes - turn them off
matplotlib.pyplot.axis('off')
img.axes.get_xaxis().set_visible(False)
img.axes.get_yaxis().set_visible(False)

# Output as pdf
matplotlib.pyplot.savefig('plot_orography_rotated.pdf', bbox_inches='tight', pad_inches = 0)
