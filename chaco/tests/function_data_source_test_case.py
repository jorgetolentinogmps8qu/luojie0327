"""
Test of basic dataseries behavior.
"""

import unittest2 as unittest

from numpy import array, linspace, nan, ones
from numpy.testing import assert_array_equal
import numpy as np

from chaco.api import DataRange1D
from chaco.function_data_source import FunctionDataSource
from traits.testing.unittest_tools import UnittestTools


class FunctionDataSourceTestCase(UnittestTools, unittest.TestCase):

    def test_init_defaults(self):
        data_source = FunctionDataSource()
        assert_array_equal(data_source._data, [])
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "ascending")
        self.assertFalse(data_source.is_masked())

    def test_basic_setup(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        assert_array_equal(myfunc, data_source.func)
        self.assertEqual(data_source.value_dimension, "scalar")
        self.assertEqual(data_source.sort_order, "ascending")
        self.assertFalse(data_source.is_masked())

    def test_set_data(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)

        with self.assertRaises(RuntimeError):
            data_source.set_data(lambda low, high: linspace(low, high, 101))

    def test_set_mask(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        mymask = array([i % 2 for i in xrange(101)], dtype=bool)

        with self.assertRaises(NotImplementedError):
            data_source.set_mask(mymask)

    def test_remove_mask(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)

        with self.assertRaises(NotImplementedError):
            data_source.remove_mask()

    def test_get_data(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        data_source.data_range = DataRange1D(low_setting=0.0, high_setting=1.0)

        assert_array_equal(linspace(0.0, 1.0, 101)**2, data_source.get_data())

    def test_get_data_no_data(self):
        data_source = FunctionDataSource()

        assert_array_equal(data_source.get_data(), array([], dtype=float))

    def test_get_data_mask(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        data_source.data_range = DataRange1D(low_setting=0.0, high_setting=1.0)

        data, mask = data_source.get_data_mask()
        assert_array_equal(data, linspace(0.0, 1.0, 101)**2)
        assert_array_equal(mask, ones(shape=101, dtype=bool))

    def test_bounds(self):
        myfunc = lambda low, high: linspace(low, high, 100)**2
        data_source = FunctionDataSource(func=myfunc)
        data_source.data_range = DataRange1D(low_setting=0.0, high_setting=2.0)

        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0.0, 4.0))

    @unittest.skip("default sort_order is ascending, which isn't right")
    def test_bounds_non_monotone(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        data_source.data_range = DataRange1D(low_setting=-2.0,
                                             high_setting=2.0)

        bounds = data_source.get_bounds()
        self.assertEqual(bounds, (0.0, 4.0))

    def test_data_size(self):
        myfunc = lambda low, high: linspace(low, high, 101)**2
        data_source = FunctionDataSource(func=myfunc)
        data_source.data_range = DataRange1D(low_setting=0.0,
                                             high_setting=2.0)

        self.assertEqual(101, data_source.get_size())
