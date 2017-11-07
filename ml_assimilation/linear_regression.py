# Show effect of asimilating more obs into 20CR

# Use vanilla linear regression

import iris
import os
import numpy
import matplotlib.pyplot
import matplotlib.colors
import Meteorographica.data.twcr as twcr
import cartopy
import cartopy.crs as ccrs
import math

# Remove incomprehensible error message
iris.FUTURE.netcdf_promote=True

# Specify the data to plot
year=1897
month=11
day=28
hour=18

# Make the plot
fig=matplotlib.pyplot.figure(facecolor=(0.78,0.78,0.78,1))

# A4 size
fig.set_size_inches(16, 22)

# set the region to plot
projection=ccrs.RotatedPole(pole_longitude=177.5, pole_latitude=37.5)
ax = matplotlib.pyplot.axes(projection=projection)
ax.set_extent([-8/math.sqrt(2)-1.5,8/math.sqrt(2)-1.5,-6,10], crs=projection)

# Set the background colour
ax.set_facecolor((0.78,0.78,0.78,1))

# Add a lat lon grid
gl_minor=ax.gridlines(linestyle='-',linewidth=0.2,color=(0,0.50,0,0.3),zorder=0)
gl_minor.xlocator = matplotlib.ticker.FixedLocator(numpy.arange(-20,20,0.5))
gl_minor.ylocator = matplotlib.ticker.FixedLocator(numpy.arange(20,80,0.5))
gl_major=ax.gridlines(linestyle='-',linewidth=1,color=(0,0.50,0,0.3),zorder=1)
gl_major.xlocator = matplotlib.ticker.FixedLocator(numpy.arange(-20,20,2))
gl_major.ylocator = matplotlib.ticker.FixedLocator(numpy.arange(20,80,2))

# Plot the land
ax.add_feature(cartopy.feature.NaturalEarthFeature('physical', 'land', '10m'), 
               edgecolor=(0.59,0.59,0.59,0),
               facecolor=(0.59,0.59,0.59,1),
               zorder=2)


# Make a dummy cube to use as a plot grid
cs=iris.coord_systems.RotatedGeogCS(37.5,177.5)
lat_values=numpy.arange(10,-6,-0.05)
latitude = iris.coords.DimCoord(lat_values,
                                standard_name='latitude',
                                units='degrees_north',
                                coord_system=cs)
lon_values=numpy.arange(-8/math.sqrt(2)-1.5,8/math.sqrt(2)-1.5,0.05)
longitude = iris.coords.DimCoord(lon_values,
                                standard_name='longitude',
                                units='degrees_east',
                                coord_system=cs)
dummy_data = numpy.zeros((len(lat_values), len(lon_values)))
plot_cube = iris.cube.Cube(dummy_data,
                           dim_coords_and_dims=[(latitude, 0),
                                                (longitude, 1)])

# Overplot the pressure as a contour plot
prmsl=twcr.get_slice_at_hour('prmsl',year,month,day,hour,
                             version='3.5.1',type='ensemble')
c2=iris.coord_systems.GeogCS(iris.fileformats.pp.EARTH_RADIUS)
prmsl.coord('latitude').coord_system=c2
prmsl.coord('longitude').coord_system=c2
prmsl.dim_coords[0].rename('member') # Can't have spaces in name
for m in numpy.arange(1,56):
    pe=prmsl.extract(iris.Constraint(member=m))
    prmsl_p = pe.regrid(plot_cube,iris.analysis.Linear())
    lats = prmsl_p.coord('latitude').points
    lons = prmsl_p.coord('longitude').points
    lons,lats = numpy.meshgrid(lons,lats)
    CS = matplotlib.pyplot.contour(lons, lats, prmsl_p.data/100,
                                   colors='blue',
                                   linewidths=0.2,
                                   levels=[970,978,986,994,1002,1010,1016],
                                   extent=[354.9107,363.3107,-3.77995,7.16005])
matplotlib.pyplot.clabel(CS, inline=1, fontsize=16, fmt='%d')

# Don't want axes - turn them off
matplotlib.pyplot.axis('off')
ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

# Output as pdf
matplotlib.pyplot.savefig('linear_regression.pdf', 
                          facecolor=(1, 1, 1),
                          bbox_inches='tight', pad_inches = 0,
                          dpi=300)
