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
The functions in this module fetch Met Office public data from AWS and
store it on $SCRATCH. And then support access to the data in those files
by date and (20CR) variable name.

See http://data.informaticslab.co.uk/ - some of this code is taken from there.
"""

import os

def load(dataset_name, variable, 
         year, month, day, hour,
         realization, forecast_period,
         auto_fetch=False):
    """Load a field from the InformaticsLab MOGREPS data

       'hour' and 'forecast_period are real variables, not
       integers - will interpolate as necessary.

       'variable' uses the 20CR naming scheme: 'air.2m', 'prmsl',
          'prate', 'uwnd.10m', ...

       If 'auto_fetch' is True, fetch files from AWS as needed, if False
        throw an exception if they are not already on local disc"""

    if(is_single_field(dataset_name, variable, 
                       year, month, day, hour,
                       realization, forecast_period)):
        return load_single_field(dataset_name, variable, 
                       year, month, day, hour,
                       realization, forecast_period,auto_fetch)

def load_single_field(dataset_name, variable, 
                      year, month, day, hour,
                      realization, forecast_period,
                      auto_fetch=False):
    """year, month, day, hour is the validity time of the field"""
    vdate=datetime.datetime(year,month,day,hour)
    fdate=vdate-datetime.timedelta(hours=forecast_period)
    # Get the file with the data in


def is_single_field(dataset_name, variable, 
                    year, month, day, hour,
                    realization, forecast_period):
    """True if data requested is in file - false if interpolation
       from multiple fields needed."""
    dataset_name=validate_dataset_name(dataset_name)
    if(validated_name == 'mogreps-g'):
        if(hour%1==0 and forecast_period%1==0):
            return True
        return False
    if(validated_name == 'mogreps-uk'):
        if(hour%1==0 and forecast_period%1==0):
            return True
        return False
    raise StandardError("Unsupported dataset %s. " % dataset_name)

def validate_dataset_name(dataset_name):
    validated_name = dataset_name.lower()
    if(validated_name != 'mogreps-g' and
       validated_name != 'mogreps-uk'):
        raise StandardError("Unsupported dataset %s. " % dataset_name +
                            "Must be 'mogreps-g or mogreps-uk")
    return validated_name

def is_file_for(dataset_name, year, month, day, hour, realization, forecast_period):
    """Is there a dump file for this set of data?"""
    dataset_name = validate_dataset_name(dataset_name)
    if dataset_name == 'mogreps-g':
        if hour%6 != 0 or hour < 0 or hour > 18:
            return False
        if realization < 0 or realization > 11:
            return False
        if (forecast_period%3 != 0 or forecast_period < 3 or
                                      forecast_period > 174):
            return False
        return True
    if dataset_name == 'mogreps-uk':
        if hour%6 != 3 or hour < 3 or hour > 21:
            return False
        if realization < 0 or realization > 22:
            return False
        if (forecast_period%3 != 0 or forecast_period < 3 or 
                                      forecast_period > 36):
            return False
        return True
    raise StandardError("Unsupported dataset %s. " % dataset_name +
                        "Must be mogreps-g or mogreps-uk")

def make_local_file_name(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    template_string = "{}/{}/{:04d}/{:02d}/{:02d}/{:02d}/"
    if os.getenv('SCRATCH') is None:
        raise StandardError("SCRATCH environment variable is not defined")
    file_name = template_string.format(os.environ['SCRATCH'],dataset_name,
                                       year, month, day, hour)
    template_string = "prods_op_{}_{:04d}{:02d}{:02d}_{:02d}_{:02d}_{:03d}.nc"
    file_name = file_name + template_string.format(dataset_name, 
                                                   year, month, day, hour,
                                                   realization, forecast_period)
    return file_name

def make_remote_url(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    template_string = "prods_op_{}_{:02d}{:02d}{:02d}_{:02d}_{:02d}_{:03d}.nc"
    file_name = template_string.format(dataset_name, year, month, day, hour,
                                       realization, forecast_period)
    url = "https://s3.eu-west-2.amazonaws.com/" + dataset_name + "/" + file_name
    return url

def fetch_data(dataset_name, year, month, day, hour, realization, forecast_period):
    dataset_name = validate_dataset_name(dataset_name)
    if not is_file_for(dataset_name, year, month, day, hour,
                       realization, forecast_period):
        raise StandardError("No data file at hour %d, realisation %d, forecast %d" %
                            (hour, realization, forecast_period))
    local_file_name = make_local_file_name(dataset_name, year, month, day, hour,
                                           realization, forecast_period)
    if os.path.isfile(local_file_name):
        return('Already fetched') # Already fetched
    local_dir = os.path.dirname(local_file_name)
    if not os.path.isdir(local_dir):
        os.makedirs(local_dir)
    remote_url = make_remote_url(dataset_name, year, month, day, hour,
                                  realization, forecast_period)
    # urllib.urlretrieve corrupted the file for some reason
    # so use wget - I like the progress bar anyway.
    os.system("wget -P %s %s" % (os.path.dirname(local_file_name),
                                 remote_url))


