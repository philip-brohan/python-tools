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
import os.path
import iris
import iris.time
import datetime
import numpy as np
import pandas

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

def get_obs_1file(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run"""
    if(version[0]=='4'):
      return get_obs_1file_v3(year,month,day,hour,version=version)
    else:
      return get_obs_1file_v2(year,month,day,hour,version=version)

def get_obs_1file_v2(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run
     Version for v2 format data."""
    base_dir=get_data_dir(version)
    of_name="%s/observations/%04d/prepbufrobs_assim_%04d%02d%02d%02d.txt" % (base_dir,
            year,year,month,day,hour)
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o=pandas.read_fwf(of_name,
                       colspecs=[(1,19),(21,23),(25,25),(27,33),(35,40),(42,46),(48,52),
                                 (54,59),(61,67),(69,75),(77,83),(85,94),(96,100),
                                 (102,106),(108,108),(110,110),(112,112),(114,114),
                                 (116,116),(118,127),(129,138),(140,149),(151,160),
                                 (162,191),(193,206)],          
                       header=None,
                       encoding="ISO-8859-1",
                       names=['UID','NCEP.Type','Variable','Longitude','Latitude',
                               'Elevation','Model.Elevation','Time.Offset',
                               'Pressure.after.bias.correction',
                               'Pressure.after.vertical.interpolation',
                               'SLP','Bias',
                               'Error.in.surface.pressure',
                               'Error.in.vertically.interpolated.pressure',
                               'Assimilation.indicator',
                               'Usability.check',
                               'QC.flag',
                               'Background.check',
                               'Buddy.check',
                               'Mean.first.guess.pressure.difference',
                               'First.guess.pressure.spread',
                               'Mean.analysis.pressure.difference',
                               'Analysis.pressure.spread',
                               'Name','ID'],
                       converters={'UID': str, 'NCEP.Type': int, 'Variable' : str,
                                   'Longitude': float,'Latitude': float,'Elevation': int,
                                   'Model.Elevation': int, 'Time.Offset': float,
                                   'Pressure.after.bias.correction': float,
                                   'Pressure.after.vertical.interpolation': float,
                                   'SLP': float,'Bias': float,
                                   'Error.in.surface.pressure': float,
                                   'Error.in.vertically.interpolated.pressure': float,
                                   'Assimilation.indicator': int,
                                   'Usability.check': int, 'QC.flag': int,
                                   'Background.check': int, 'Buddy.check': int,
                                   'Mean.first.guess.pressure.difference': float,
                                   'First.guess.pressure.spread': float,
                                   'Mean.analysis.pressure.difference': float,
                                   'Analysis.pressure.spread': float,
                                   'Name': str, 'ID': str},
                       na_values=['NA','*','***','*****','*******','**********',
                                          '-99','9999','-999','9999.99','10000.0',
                                          '-9.99','999999999999999999999999999999',
                                          '999999999999','9'],
                       comment=None)
    return(o)

def get_obs_1file_v3(year,month,day,hour,version):
    """Retrieve all the observations for an individual assimilation run
     Version for v3 format data."""
    base_dir=get_data_dir(version)
    of_name="%s/observations/%04d/%02d/psobfile_%04d%02d%02d%02d" % (base_dir,
            year,month,year,month,day,hour)
    if not os.path.isfile(of_name):
        raise IOError("No obs file for given version and date")

    o=pandas.read_fwf(of_name,
                       colspecs=[(1,19),(21,23),(25,25),(27,33),(35,40),(42,46),
                                 (48,53),(55,62),(64,71),(73,78),(80,109)],
                       usecols=[0,1,2,3,4,5,6,7,8,9,10],
                       header=None,
                       encoding="ISO-8859-1",
                       names=['UID','NCEP.Type','Variable','Longitude','Latitude',
                              'Un1','Un2','Un3','Un4','Un5','Name'],
                       converters={'UID': str, 'NCEP.Type': int, 'Variable' : str,
                                   'Longitude': float, 'Latitude': float, 'Un1': int,
                                   'Un2': float, 'Un3': float, 'Un4': float,
                                   'Un5': float, 'Name': str},
                       na_values=['NA','*','***','*****','*******','**********',
                                          '-99','9999','-999','9999.99','10000.0',
                                          '-9.99','999999999999999999999999999999',
                                          '999999999999','9'],
                       comment=None)
    return(o)
 
def get_obs(start,end,version):
    """Retrieve all the observations between start and end"""
    base_dir=get_data_dir(version)
    result=None
    ct=start
    while(ct<end):
        of_name="%s/observations/%04d/prepbufrobs_assim_%04d%02d%02d%02d.txt" : (base.dir,
                ct.year,ct.year,ct.month,ct.day,ct,hour)
        if(version[0]=='4'):
           of_name="%s/observations/%04d/%02d/psobfile_%04d%02d%02d%02d" : (base.dir,
                ct.year,ct.month,ct.year,ct.month,ct.day,ct,hour)
        if not os.path.isfile(of_name):
           continue
        o=get_obs_1file(ct.year,ct.month,ct.day,ct,hour,version)
        odates=o.apply(
