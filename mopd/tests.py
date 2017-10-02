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
 
    def test_name_validate(self):
        self.assertEqual(mopd.validate_dataset_name('mogreps-g'),
                         'mogreps-g')
        self.assertEqual(mopd.validate_dataset_name('MOGREPS-G'),
                         'mogreps-g')
        with self.assertRaises(StandardError):
            mopd.validate_dataset_name('MOGREPSG')

    def test_is_file_for(self):
        self.assertTrue(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,2,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,24,0,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,0,0,0))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,0,175))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                          2016,3,12,0,0,4))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,-1,3))
        self.assertFalse(mopd.is_file_for('mogreps-g',
                                         2016,3,12,0,12,3))
        with self.assertRaises(StandardError):
            mopd.is_file_for('mogrepsg',
                              2016,3,12,0,0,0)


if __name__ == '__main__':
    unittest.main()

