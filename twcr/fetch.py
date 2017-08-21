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
The functions in this module fetch 20CR data from NERSC and
store it on $SCRATCH.

It requires scp access to private files
at NERSC - it will only work for Philip.
"""

import os
import subprocess

def 

def fetch_data_for_month(variable,year,month,
                         version,type='ensemble'):
 """Version 3 specific - for version 2 use fetch_data_for_year."""
    variable=variable.lower()
    local_file=get_data_file_name(variable,year,month,version,type)
    if os.path.isfile(local_file):
        return
    remote_file=get_remote_file_name(variable,year,month,version,type)
    cmd="scp %s %s" % (remote.file,local_file)
    scp_retvalue=subprocess.call(cmd)
    if scp_retvalue!=0:
        raise Error("Failed to retrieve data")

