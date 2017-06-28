# (C) British Crown Copyright 2017, Met Office
#
# This code is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This code is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
"""
The functions in this module provide the main way to load and/or save
20CR data.
"""

import os
import datetime
import iris
import iris.time

def get_data_dir(version):
    """Return the root directory containing 20CR netCDF files"""
    g=sprintf("%s/20CR/version_%s/",os.environ('SCRATCH'),version)
    if os.path.isdir(sprintf(g)):
        return g
    g=sprintf("/project/projectdirs/m958/netCDF.data/20CR_v%s/",
               version)
    if os.path.isdir(sprintf(g)):
        return g
    raise IOError(sprintf("No data found for version %s",version))

def get_data_file_name(variable,year,month,day,hour,version,
                       type='ensemble'):
    """Return the name of the file containing data for the
       requested variabe, at the specified time, from the
       20CR version."""
    base.dir=get_data_dir(version)
    name=None
    if type=='normal':
        name=sprintf("%s/hourly/normals/%s.nc",base.dir,variable)
    if type=='standard.deviation':
        name<-sprintf("%s/hourly/standard.deviations/%s.nc",
                      base.dir,variable)
    if type=='ensemble':
        if version[0]==4: # V3 data is by month
            name=sprintf("%s/hourly/%04d/%02d/%s.nc",base.dir,
                          year,month,variable)
        else:              # V2 data is by year
            name=sprintf("%s/ensembles/hourly/%04d/%s.nc",base.dir,
                          year,variable)
    if name==None:
       raise IOError(sprintf("Unsupported type %s",type))
    return name

def is_in_file(variable,version,hour):
    """Is the variable avaialble for this time?

       Or will it have to be interpolated?"""
    if(version[0]==4 and hour%3==0):
        return 'True'
    if hour%6==0:
        return 'True'
    return 'False'

def get_slice_at_hour(variable,year,month,day,hour,version,
                      type='ensemble'):
    if not is_in_file(variable,version,hour):
        raise ValueError("Invalid hour - data not in file")
    file_name=get_data_file_name(variable,year,month,day,hour,
                                 version,type)
    time_constraint=iris.Constraint(time=iris.time.PartialDateTime(
                                   year=year,
                                   month=month,
                                   day=day,
                                   hour=hour))
    try:
        hslice=iris.load_cube(file_name,
                             time.constraint)
    except iris.exceptions.ConstraintMismatchError:
       print("Data not available")
    return hslice
