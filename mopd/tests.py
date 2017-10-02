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
Test cases for the mopd module.

Run python on this file to run all the tests.
"""
import mopd
import unittest

class TestUM(unittest.TestCase):
 
    def test_name_mgg(self):
        self.assertEqual(mopd.validate_dataset_name('mogreps-g'),
                         'mogreps-g')


if __name__ == '__main__':
    unittest.main()

