"""
Unittests for gj2ascii.core
"""


from collections import OrderedDict
import itertools
import os
import unittest

import emoji
import fiona as fio
import pytest

import gj2ascii
import gj2ascii.core
import numpy as np


@pytest.fixture(scope='function')
def geo_interface_feature():

    class GIFeature(object):
        __geo_interface__ = {
            'type': 'Feature',
            'properties': {},
            'geometry': {
                'type': 'Point',
                'coordinates': [10, 20, 30]
            }
        }
    return GIFeature()


@pytest.fixture(scope='function')
def geo_interface_geometry():
    class GIGeometry(object):
        __geo_interface__ = {
            'type': 'Polygon',
            'coordinates': [[(1.23, -56.5678), (4.897, 20.937), (9.9999999, -23.45)]]
        }
    return GIGeometry()


@pytest.fixture(scope='function')
def feature():
    return {
        'type': 'Feature',
        'properties': {},
        'geometry': {
            'type': 'Line',
            'coordinates': ((1.23, -67.345), (87.12354, -23.4555), (123.876, -78.9444))
        }
    }


@pytest.fixture(scope='function')
def geometry():
    return {
        'type': 'Point',
        'coordinates': (0, 0, 10)
    }


@pytest.fixture(scope='function')
def ascii():
    return os.linesep.join([
        '* * * * *',
        '  *   *  ',
        '* * * * *'
    ])


@pytest.fixture(scope='function')
def array():
    return [
        ['*', '*', '*', '*', '*'],
        [' ', '*', ' ', '*', ' '],
        ['*', '*', '*', '*', '*']]


@pytest.fixture(scope='function')
def np_array(array):
    return np.array(array)


def test_compare_ascii(compare_ascii):
    block = """
    line1
    line2
    something
    a n o t h e r line
    None
    6789.2349
    """
    assert compare_ascii(block, block) is True


def test_dict2table_empty_dict():
    with pytest.raises(ValueError):
        gj2ascii.dict2table({})


def test_dict2table():
    test_dict = OrderedDict((
        ('Field1', None),
        ('__something', 'a string'),
        ('more', 12345),
        ('other', 1.2344566)
    ))
    expected = """
+-------------+-----------+
| Field1      |      None |
| __something |  a string |
| more        |     12345 |
| other       | 1.2344566 |
+-------------+-----------+
""".strip()
    assert gj2ascii.dict2table(test_dict) == expected


def test_render_exception():
    with pytest.raises(TypeError):
        gj2ascii.render([], None, fill='asdf')
    with pytest.raises(TypeError):
        gj2ascii.render([], None, char='asdf')
    with pytest.raises(ValueError):
        gj2ascii.render([], width=-1)


def test_render_compare_bbox_given_vs_detect_collection_vs_compute_vs_as_generator(poly_file):
    # Easiest to compare these 3 things together since they are related
    with fio.open(poly_file) as src:
        given = gj2ascii.render(src, 15, bbox=src.bounds)
        computed = gj2ascii.render([i for i in src], 15)
        fio_collection = gj2ascii.render(src, 15)
        # Passing in a generator and not specifying x/y min/max requires the features to
        # be iterated over twice which is a problem because generators cannot be reset.
        # A backup of the generator should be created automatically and iterated over the
        # second time.
        generator_output = gj2ascii.render((f for f in src), 15)
    for pair in itertools.combinations(
            [given, computed, fio_collection, generator_output], 2):
        assert len(set(pair)) == 1


def test_with_fio(expected_polygon_40_wide, poly_file):
    with fio.open(poly_file) as src:
        r = gj2ascii.render(src, width=40, fill='.', char='+', bbox=src.bounds)
        assert expected_polygon_40_wide == r.rstrip()


def test_geometry_extractor_exceptions():
    with pytest.raises(TypeError):
        next(gj2ascii.core._geometry_extractor([{'type': None}]))


def test_single_object(geometry, feature, geo_interface_feature, geo_interface_geometry):
    assert geometry == next(gj2ascii.core._geometry_extractor(geometry))
    assert feature['geometry'] == next(gj2ascii.core._geometry_extractor(feature))
    assert geo_interface_feature.__geo_interface__['geometry'] == next(gj2ascii.core._geometry_extractor(geo_interface_feature))
    assert geo_interface_geometry.__geo_interface__ == next(gj2ascii.core._geometry_extractor(geo_interface_geometry))


def test_multiple_homogeneous(geometry, feature, geo_interface_geometry, geo_interface_feature):

    for item in gj2ascii.core._geometry_extractor(
            (geometry, geometry, geometry)):
        assert item == geometry

    for item in gj2ascii.core._geometry_extractor(
            (feature, feature, feature)):
        assert item == feature['geometry']

    for item in gj2ascii.core._geometry_extractor(
            (geo_interface_geometry, geo_interface_geometry, geo_interface_geometry)):
        assert item == geo_interface_geometry.__geo_interface__

    for item in gj2ascii.core._geometry_extractor(
            (geo_interface_feature, geo_interface_feature, geo_interface_feature)):
        assert item == geo_interface_feature.__geo_interface__['geometry']


def test_multiple_heterogeneous(geometry, feature, geo_interface_feature, geo_interface_geometry):
    input_objects = (geometry, feature, geo_interface_feature, geo_interface_geometry)
    expected = (
        geometry, feature['geometry'],
        geo_interface_feature.__geo_interface__['geometry'],
        geo_interface_geometry.__geo_interface__
    )
    for expected, actual in zip(
            expected, gj2ascii.core._geometry_extractor(input_objects)):
        assert expected == actual


def test_standard():

    l1 = gj2ascii.array2ascii([['*', '*', '*', '*', '*'],
                               [' ', ' ', '*', ' ', ' '],
                               ['*', '*', ' ', ' ', ' ']])

    l2 = gj2ascii.array2ascii([[' ', ' ', ' ', '+', '+'],
                               [' ', '+', ' ', ' ', ' '],
                               [' ', ' ', '+', '+', '+']])

    eo = gj2ascii.array2ascii([['*', '*', '*', '+', '+'],
                               ['.', '+', '*', '.', '.'],
                               ['*', '*', '+', '+', '+']])

    assert gj2ascii.stack(
        [l1, l2], fill='.').strip(os.linesep), eo.strip(os.linesep)


def test_exceptions():
    # Bad fill value
    with pytest.raises(ValueError):
        gj2ascii.stack([], fill='too-long')

    # Input layers have different dimensions
    with pytest.raises(ValueError):
        gj2ascii.stack(['1', '1234'])


def test_single_layer(compare_ascii):
    l1 = gj2ascii.array2ascii([['*', '*', '*', '*', '*'],
                               [' ', ' ', '*', ' ', ' '],
                               ['*', '*', ' ', ' ', ' ']])

    assert compare_ascii(l1, gj2ascii.stack([l1]))


def test_ascii2array(array, ascii):
    assert array == gj2ascii.ascii2array(ascii)
    assert np.array_equal(array, np.array(gj2ascii.ascii2array(ascii)))


def test_array2ascii(ascii, array):
    assert ascii == gj2ascii.array2ascii(array)
    assert ascii == gj2ascii.array2ascii(array)


def test_roundhouse(ascii, array):
    assert ascii == gj2ascii.array2ascii(gj2ascii.ascii2array(ascii))
    assert array == gj2ascii.ascii2array(gj2ascii.array2ascii(array))


def test_style():

    array = [['0', '0', '0', '1', '0'],
             [' ', ' ', '2', '0', '1'],
             ['1', '1', '2', '1', '3']]
    colormap = {
        ' ': 'black',
        '0': 'blue',
        '1': 'yellow',
        '2': 'white',
        '3': 'red'
    }
    expected = []
    for row in array:
        o_row = []
        for char in row:
            color = gj2ascii.ANSI_COLORMAP[colormap[char]]
            o_row.append(color + char + ' ' + gj2ascii.core._ANSI_RESET)
        expected.append(''.join(o_row))
    expected = os.linesep.join(expected)
    assert expected == gj2ascii.style(gj2ascii.array2ascii(array), stylemap=colormap)


def test_paginate(poly_file):

    char = '+'
    fill = '.'
    colormap = {
        '+': 'red',
        '.': 'black'
    }
    with fio.open(poly_file) as src1, fio.open(poly_file) as src2:
        for paginated_feat, feat in zip(
                gj2ascii.paginate(src1, char=char, fill=fill, colormap=colormap), src2):
            assert paginated_feat.strip() == gj2ascii.style(
                gj2ascii.render(feat, char=char, fill=fill), stylemap=colormap)


def test_bbox_from_arbitrary_iterator(poly_file):

    # Python 2 doesn't give direct access to an object that can be used to check if an object
    # is an instance of tee
    pair = itertools.tee(range(10))
    itertools_tee_type = pair[1].__class__

    with fio.open(poly_file) as c_src, \
            fio.open(poly_file) as l_src, \
            fio.open(poly_file) as g_src,\
            fio.open(poly_file) as expected:
        # Tuple element 1 is an iterable object to test and element 2 is the expected type of
        # the output iterator
        test_objects = [
            (c_src, fio.Collection),
            ([i for i in l_src], list),
            ((i for i in g_src), itertools_tee_type)
        ]
        for in_obj, e_type in test_objects:
            bbox, iterator = gj2ascii.core.min_bbox(in_obj, return_iter=True)
            assert bbox == expected.bounds, \
                "Bounds don't match: %s != %s" % (bbox, expected.bounds)
            assert isinstance(iterator, e_type), "Output iterator is %s" % iterator
            for e, a in zip(expected, iterator):
                assert e['id'] == a['id'], "%s != %s" % (e['id'], a['id'])


def test_render_multiple(poly_file, line_file, point_file, compare_ascii):
    with fio.open(poly_file) as poly, \
            fio.open(line_file) as lines, \
            fio.open(point_file) as points:

        coords = list(poly.bounds) + list(lines.bounds) + list(points.bounds)
        bbox = (min(coords[0::4]), min(coords[1::4]), max(coords[2::4]), max(coords[3::4]))

        width = 20
        lyr_char_pairs = [(poly, '+'), (lines, '-'), (points, '*')]
        actual = gj2ascii.render_multiple(lyr_char_pairs, width, fill='#')

        rendered_layers = []
        for l, char in lyr_char_pairs:
            rendered_layers.append(gj2ascii.render(l, width, fill=' ', bbox=bbox, char=char))
        expected = gj2ascii.stack(rendered_layers, fill='#')

        assert compare_ascii(actual.strip(), expected.strip())


def test_render_exceptions():
    for arg in ('fill', 'char'):
        with pytest.raises(ValueError):
            gj2ascii.render([], **{arg: 'too long'})
    for w in (0, -1, -1000):
        with pytest.raises(ValueError):
            gj2ascii.render([], width=w)


def test_style_multiple(poly_file, line_file, point_file):
    with fio.open(poly_file) as poly, \
            fio.open(line_file) as lines, \
            fio.open(point_file) as points:

        coords = list(poly.bounds) + list(lines.bounds) + list(points.bounds)
        bbox = (min(coords[0::4]), min(coords[1::4]), max(coords[2::4]), max(coords[3::4]))

        width = 20

        # Mix of colors and emoji with a color fill
        lyr_color_pairs = [(poly, ':+1:'), (lines, 'blue'), (points, 'red')]
        actual = gj2ascii.style_multiple(
            lyr_color_pairs, fill='yellow', width=width, bbox=bbox)
        assert emoji.unicode_codes.EMOJI_ALIAS_UNICODE[':+1:'] in actual
        assert '\x1b[34m\x1b[44m' in actual  # blue
        assert '\x1b[31m\x1b[41m' in actual  # red
        assert '\x1b[33m\x1b[43m' in actual  # yellow

        # Same as above but single character fill
        lyr_color_pairs = [(poly, ':+1:'), (lines, 'blue'), (points, 'red')]
        actual = gj2ascii.style_multiple(
            lyr_color_pairs, fill='.', width=width, bbox=bbox)
        assert emoji.unicode_codes.EMOJI_ALIAS_UNICODE[':+1:'] in actual
        assert '\x1b[34m\x1b[44m' in actual  # blue
        assert '\x1b[31m\x1b[41m' in actual  # red
        assert '.' in actual

        # Same as above but emoji fill
        lyr_color_pairs = [(poly, ':+1:'), (lines, 'blue'), (points, 'red')]
        actual = gj2ascii.style_multiple(
            lyr_color_pairs, fill=':water_wave:', width=width, bbox=bbox)
        assert emoji.unicode_codes.EMOJI_ALIAS_UNICODE[':+1:'] in actual
        assert '\x1b[34m\x1b[44m' in actual  # blue
        assert '\x1b[31m\x1b[41m' in actual  # red
        assert emoji.unicode_codes.EMOJI_ALIAS_UNICODE[':water_wave:'] in actual
