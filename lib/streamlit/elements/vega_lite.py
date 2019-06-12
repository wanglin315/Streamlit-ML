# Copyright 2018 Streamlit Inc. All rights reserved.

"""A Python wrapper around Vega-Lite."""

# Python 2/3 compatibility
from __future__ import print_function, division, unicode_literals, absolute_import
from streamlit.compatibility import setup_2_3_shims
setup_2_3_shims(globals())

import json

import streamlit.elements.lib.dicttools as dicttools
import streamlit.elements.data_frame_proto as data_frame_proto

from streamlit.logger import get_logger
LOGGER = get_logger(__name__)


def marshall(proto, data=None, spec=None, **kwargs):
    """Construct a Vega-Lite chart object.

    See DeltaGenerator.vega_lite_chart for docs.
    """
    # Support passing data inside spec['datasets'] and spec['data'].
    # (The data gets pulled out of the spec dict later on.)
    if type(data) in dict_types and spec is None:
        spec = data
        data = None
        if not _looks_like_vega_lite_spec(spec):
            raise ValueError('Invalid Vega-Lite chart spec: %s' % spec)

    # Support passing in kwargs. Example:
    #   marshall(proto, {foo: 'bar'}, baz='boz')
    if len(kwargs):
        # Support passing no spec arg, but filling it with kwargs.
        # Example:
        #   marshall(proto, baz='boz')
        if spec is None:
            spec = dict()

        # Merge spec with unflattened kwargs, where kwargs take precedence.
        # This only works for string keys, but kwarg keys are strings anyways.
        spec = dict(spec, **dicttools.unflatten(kwargs, _CHANNELS))

    if spec is None or len(spec) == 0:
        raise ValueError('Vega-Lite charts require a non-empty spec dict.')

    # Pull data out of spec dict when it's in a 'dataset' key:
    #   marshall(proto, {datasets: {foo: df1, bar: df2}, ...})
    if 'datasets' in spec:
        for k, v in spec['datasets'].items():
            dataset = proto.datasets.add()
            dataset.name = str(k)
            dataset.has_name = True
            data_frame_proto.marshall_data_frame(v, dataset.data)
        del spec['datasets']

    # Pull data out of spec dict when it's in a top-level 'data' key:
    #   marshall(proto, {data: df})
    #   marshall(proto, {data: {values: df, ...}})
    #   marshall(proto, {data: {url: 'url'}})
    #   marshall(proto, {data: {name: 'foo'}})
    if 'data' in spec:
        data_spec = spec['data']

        if type(data_spec) in dict_types:
            if 'values' in data_spec:
                data = data_spec['values']
                del data_spec['values']
        else:
            data = data_spec
            del spec['data']

    proto.spec = json.dumps(spec)

    if data is not None:
        data_frame_proto.marshall_data_frame(data, proto.data)


def _looks_like_vega_lite_spec(spec):
    # Vega-Lite specs require both a 'mark' key and a 'data' key. Here we only
    # check for 'mark' because we allow passing in the data separately.
    return 'mark' in spec


# See https://vega.github.io/vega-lite/docs/encoding.html
_CHANNELS = set([
    'x',
    'y',
    'x2',
    'y2',
    'xError',
    'yError2',
    'xError',
    'yError2',
    'longitude',
    'latitude',
    'color',
    'opacity',
    'fillOpacity',
    'strokeOpacity',
    'strokeWidth',
    'size',
    'shape',
    'text',
    'tooltip',
    'href',
    'key',
    'order',
    'detail',
    'facet',
    'row',
    'column',
])