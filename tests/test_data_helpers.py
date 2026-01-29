import pytest

from scotclimpact.data_helpers import xarray_to_geojson, is_number, validate_args


@pytest.mark.parametrize(
    ('input', 'result'),
    [
        ('', False),
        ('1a', False),
        ('.', False),
        ('1', True),
        ('12', True),
        ('1.1', True),
        ('11.1', True),
        ('11.21', True),
        ('11.', True),
        ('.11', True),
        ('11.21.', False),
        ('11.21.5', False),
        ('NaN', False),
        ('Inf', False),
        ('-Inf', False),
    ]
)
def test_is_number(input, result):
    result and float(input) # if result is True, float should not throw exceptions
    assert is_number(input) == result 

#@pytest.mark.parametrize()
def test_validate_args():

    @validate_args(
        ('a', is_number, int),
        ('b', is_number, int),
        ('c', is_number, int),
    )
    def test(a, b, c='10'):
        return f'{a+b+c}', 200

    assert test('10', '20', c='10') == ('40', 200)
    assert test('x', '20')[1] == 400
    #assert test('a', 'b')[1] == 400


