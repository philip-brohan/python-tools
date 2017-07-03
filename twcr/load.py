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
The functions in this module provide the main way to load
20CR data.
"""

import os
import iris
import iris.time
import datetime
import numpy

# Eliminate incomprehensible warning message
iris.FUTURE.netcdf_promote='True'

def get_data_dir(version):
    """Return the root directory containing 20CR netCDF files"""
    g="%s/20CR/version_%s/" % (os.environ['SCRATCH'],version)
    if os.path.isdir(g):
        return g
    g="/project/projectdirs/m958/netCDF.data/20CR_v%s/" % version
    if os.path.isdir(g):
        return g
    raise IOError("No data found for version %s" % version)

def get_data_file_name(variable,year,month,day,hour,version,
                       type='ensemble'):
    """Return the name of the file containing data for the
       requested variabe, at the specified time, from the
       20CR version."""
    base_dir=get_data_dir(version)
    name=None
    if type=='normal':
        name="%s/hourly/normals/%s.nc" % (base_dir,variable)
    if type=='standard.deviation':
        name="%s/hourly/standard.deviations/%s.nc" % (base_dir,
                                                      variable)
    if type == 'ensemble':
        if version[0]=='4': # V3 data is by month
            name="%s/hourly/%04d/%02d/%s.nc" % (base_dir,
                                                year,month,
                                                variable)
        else:              # V2 data is by year
            name="%s/ensembles/hourly/%04d/%s.nc" % (base_dir,
                                                     year,
                                                     variable)
    if name==None:
       raise IOError("Unsupported type %s" % type)
    return name

def is_in_file(variable,version,hour):
    """Is the variable available for this time?
       Or will it have to be interpolated?"""
    if(version[0]=='4' and hour%3==0):
        return 'True'
    if hour%6==0:
        return 'True'
    return 'False'

def get_previous_field_time(variable,year,month,day,hour,version):
    """Get the latest time, before the given time,
                     for which there is saved data"""
    if version[0]=='4':
        return {'year':year,'month':month,'day':day,'hour':int(hour/3)*3}
    return {'year':year,'month':month,'day':day,'hour':int(hour/6)*6}

def get_next_field_time(variable,year,month,day,hour,version):
    """Get the earliest time, after the given time,
                     for which there is saved data"""
    dr = {'year':year,'month':month,'day':day,'hour':int(hour/6)*6+6}
    if version[0]=='4':
        dr = {'year':year,'month':month,'day':day,'hour':int(hour/3)*3+3}
    if dr['hour']>=24:
        d_next= ( datetime.date(dr['year'],dr['month'],dr['day']) 
                 + datetime.timedelta(1) )
        dr = {'year':d1.year,'month':d1.month,'day':d1.day,
              'hour':dr['hour']-24}
    return dr

def get_slice_at_hour_at_timestep(variable,year,month,day,hour,version,
                                  type='ensemble'):
    """Get the cube with the data, given that the specified time
       matches a data timestep."""
    if not is_in_file(variable,version,hour):
        raise ValueError("Invalid hour - data not in file")
    file_name=get_data_file_name(variable,year,month,day,hour,
                                 version,type)
    if type == 'normal' or type == 'standard.deviation':
        year=1981
        if month==2 and day==29:
            day=28
    time_constraint=iris.Constraint(time=iris.time.PartialDateTime(
                                   year=year,
                                   month=month,
                                   day=day,
                                   hour=hour))
    try:
        with iris.FUTURE.context(cell_datetime_objects=True):
            hslice=iris.load_cube(file_name,
                                  time_constraint)
    # This isn't the right error to catch
    except iris.exceptions.ConstraintMismatchError:
       print("Data not available")
    return hslice

def get_slice_at_hour(variable,year,month,day,hour,version,
                      type='ensemble'):
    """Get the cube with the data, interpolating between timesteps
       if necessary."""
    if is_in_file(variable,version,hour):
        return(get_slice_at_hour_at_timestep(variable,year,
                                             month,day,
                                             hour,version,type))
    previous_step=get_previous_field_time(variable,year,month,
                                          day,hour,version)
    next_step=get_next_field_time(variable,year,month,
                                  day,hour,version)
    dt_current=datetime.datetime(year,month,day,int(hour),int((hour%1)*60))
    dt_previous=datetime.datetime(previous_step['year'],
                                  previous_step['month'],
                                  previous_step['day'],
                                  previous_step['hour'])
    dt_next=datetime.datetime(next_step['year'],
                              next_step['month'],
                              next_step['day'],
                              next_step['hour'])
    weight=((dt_current-dt_previous).total_seconds()
            /(dt_next-dt_previous).total_seconds())
    s_previous=get_slice_at_hour_at_timestep(variable,
                                             previous_step['year'],
                                             previous_step['month'],
                                             previous_step['day'],
                                             previous_step['hour'],
                                             version,type)
    s_next=get_slice_at_hour_at_timestep(variable,
                                         next_step['year'],
                                         next_step['month'],
                                         next_step['day'],
                                         next_step['hour'],
                                         version,type)
    s_next.data=s_next.data*weight+s_previous.data*(1-weight)
    return s_next

