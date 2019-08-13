# Copyright 2019 Streamlit Inc. All rights reserved.
# -*- coding: utf-8 -*-

"""st.hashing unit tests."""

import functools
import sys
import tempfile
import unittest

import altair as alt
import pandas as pd
import pytest

import streamlit as st
from streamlit.hashing import get_hash


class HashTest(unittest.TestCase):
    def test_string(self):
        self.assertEqual(get_hash('hello'), get_hash('hello'))
        self.assertNotEqual(get_hash('hello'), get_hash('hellö'))

    def test_int(self):
        self.assertEqual(get_hash(145757624235), get_hash(145757624235))
        self.assertNotEqual(get_hash(10), get_hash(11))
        self.assertNotEqual(get_hash(-1), get_hash(1))
        self.assertNotEqual(get_hash(2**7), get_hash(2**7-1))
        self.assertNotEqual(get_hash(2**7), get_hash(2**7+1))

    def test_list(self):
        self.assertEqual([1, 2], [1, 2])
        self.assertNotEqual([1, 2], [2, 2])
        self.assertNotEqual([1], 1)

    def test_tuple(self):
        self.assertEqual((1, 2), (1, 2))
        self.assertNotEqual((1, 2), (2, 2))
        self.assertNotEqual((1,), 1)
        self.assertNotEqual((1,), [1])

    def test_float(self):
        self.assertEqual(get_hash(0.1), get_hash(0.1))
        self.assertNotEqual(get_hash(23.5234), get_hash(23.5235))

    def test_bool(self):
        self.assertEqual(get_hash(True), get_hash(True))
        self.assertNotEqual(get_hash(True), get_hash(False))

    def test_none(self):
        self.assertEqual(get_hash(None), get_hash(None))
        self.assertNotEqual(get_hash(None), get_hash(False))

    def test_builtins(self):
        self.assertEqual(get_hash(abs), get_hash(abs))
        self.assertNotEqual(get_hash(abs), get_hash(type))

    def test_pandas(self):
        df1 = pd.DataFrame({'foo': [12]})
        df2 = pd.DataFrame({'foo': [42]})
        df3 = pd.DataFrame({'foo': [12]})

        self.assertEqual(get_hash(df1), get_hash(df3))
        self.assertNotEqual(get_hash(df1), get_hash(df2))

    def test_lambdas(self):
        # self.assertEqual(get_hash(lambda x: x.lower()), get_hash(lambda x: x.lower()))
        self.assertNotEqual(get_hash(lambda x: x.lower()), get_hash(lambda x: x.upper()))

    def test_files(self):
        temp1 = tempfile.NamedTemporaryFile()
        temp2 = tempfile.NamedTemporaryFile()

        with open(__file__, 'r') as f:
            with open(__file__, 'r') as g:
                self.assertEqual(get_hash(f), get_hash(g))

            self.assertNotEqual(get_hash(f), get_hash(temp1))

        self.assertEqual(get_hash(temp1), get_hash(temp1))
        self.assertNotEqual(get_hash(temp1), get_hash(temp2))

    def test_file_position(self):
        with open(__file__, 'r') as f:
            h1 = get_hash(f)
            self.assertEqual(h1, get_hash(f))
            f.readline()
            self.assertNotEqual(h1, get_hash(f))
            f.seek(0)
            self.assertEqual(h1, get_hash(f))


class CodeHashTest(unittest.TestCase):
    def test_simple(self):
        """Test the hash of simple functions."""
        def f(x):
            return x * x

        def g(x):
            return x + x

        def h(x):
            return x*x

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_rename(self):
        """Test the hash of function with renamed variables."""
        def f(x, y):
            return x + y

        def g(x, y):
            return y + x

        def h(y, x):
            return y + x

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_value(self):
        """Test the hash of functions with values."""
        def f():
            x = 42
            return x

        def g():
            x = 12
            return x

        def h():
            y = 42
            return y

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_defaults(self):
        """Test the hash of functions with defaults."""
        def f(x=42):
            return x

        def g(x=12):
            return x

        def h(x=42):
            return x

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_referenced(self):
        """Test the hash of functions that reference values."""

        x = 42
        y = 123

        def f():
            return x

        def g():
            return y

        def h():
            return x

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_referenced_referenced(self):
        """Test that we can follow references."""

        def hash_prog_1():
            x = 12

            def g():
                return x

            def f():
                return g()

            return get_hash(f)

        def hash_prog_2():
            x = 42

            def g():
                return x

            def f():
                return g()

            return get_hash(f)

        self.assertNotEqual(hash_prog_1(), hash_prog_2())

    def test_builtins(self):
        """Tes code with builtins."""

        def code_with_print():
            print(12)

        def code_with_type():
            type(12)

        self.assertNotEqual(get_hash(code_with_print), get_hash(code_with_type))

    def test_pandas_df(self):
        """Test code that references pandas dataframes."""

        def hash_prog_1():
            df = pd.DataFrame({'foo': [12]})

            def f():
                return df
            return get_hash(f)

        def hash_prog_2():
            df = pd.DataFrame({'foo': [42]})

            def f():
                return df
            return get_hash(f)

        def hash_prog_3():
            df = pd.DataFrame({'foo': [12]})

            def f():
                return df
            return get_hash(f)

        self.assertNotEqual(hash_prog_1(), hash_prog_2())
        self.assertEqual(hash_prog_1(), hash_prog_3())

    def test_lambdas(self):
        """Test code with different lambdas produces different hashes."""

        v42 = 42
        v123 = 123

        def f1():
            lambda x: v42

        def f2():
            lambda x: v123

        self.assertNotEqual(get_hash(f1), get_hash(f2))

    def test_lambdas_calls(self):
        """Test code with lambdas that call functions."""

        def f_lower():
            lambda x: x.lower()

        def f_upper():
            lambda x: x.upper()

        def f_lower2():
            lambda x: x.lower()

        self.assertNotEqual(get_hash(f_lower), get_hash(f_upper))
        self.assertEqual(get_hash(f_lower), get_hash(f_lower2))

    def test_dict_reference(self):
        """Test code with lambdas that call a dictionary."""

        a = {
            'foo': 42,
            'bar': {
                'baz': 12
            }
        }

        def f():
            return a['bar']['baz']

        def g():
            return a['foo']

        def h():
            return a['bar']['baz']

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_external_module(self):
        """Test code that references an external module."""

        def call_altair_concat():
            return alt.vegalite.v3.api.concat()

        def call_altair_layer():
            return alt.vegalite.v3.api.layer()

        self.assertNotEqual(get_hash(call_altair_concat), get_hash(call_altair_layer))

    def test_import(self):
        """Test code that imports module."""

        def f():
            import numpy
            return numpy

        def g():
            import pandas
            return pandas

        def n():
            import foobar
            return foobar

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertNotEqual(get_hash(f), get_hash(n))

    def test_class(self):
        """Test hash for classes is we call different functions."""

        x = 12
        y = 13

        class Foo():
            def get_x(self):
                return x

            def get_y(self):
                return y

        def hash_prog_1():
            o = Foo()

            def f():
                return o.get_x()

            return get_hash(f)

        def hash_prog_2():
            o = Foo()

            def f():
                return o.get_y()

            return get_hash(f)

        def hash_prog_3():
            o = Foo()

            def f():
                return o.get_x()

            return get_hash(f)

        self.assertNotEqual(hash_prog_1(), hash_prog_2())
        self.assertEqual(hash_prog_1(), hash_prog_3())

    @pytest.mark.skipif(sys.version_info < (3,), reason="Requires Python 3.")
    def test_class_referenced(self):
        """Test hash for classes with methods that reference values."""

        def hash_prog_1():
            class Foo():
                x = 12

                def get_x(self):
                    return self.x

            o = Foo()

            def f():
                return o.get_x()

            return get_hash(f)

        def hash_prog_2():
            class Foo():
                x = 42

                def get_x(self):
                    return self.x

            o = Foo()

            def f():
                return o.get_x()

            return get_hash(f)

        self.assertNotEqual(hash_prog_1(), hash_prog_2())

    def test_coref(self):
        """Test code that references itself."""

        def f(x):
            return f(x)

        def g(x):
            return g(x) + 1

        def h(x):
            return h(x)

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_multiple(self):
        """Test code that references multiple objects."""

        x = 12
        y = 13
        z = 14

        def f():
            return x + z

        def g():
            return y + z

        def h():
            return x + z

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_decorated(self):
        """Test decorated functions."""

        def do(func):
            @functools.wraps(func)
            def wrapper_do(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper_do

        @do
        def f():
            return 42

        @do
        def g():
            return 12

        @do
        def h():
            return 42

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))

    def test_cached(self):
        """Test decorated functions."""
        @st.cache
        def f():
            return 42

        @st.cache
        def g():
            return 12

        @st.cache
        def h():
            return 42

        self.assertNotEqual(get_hash(f), get_hash(g))
        self.assertEqual(get_hash(f), get_hash(h))
