import pytest


@pytest.mark.parametrize(["field", 'obj', 'val'],
                         [
                             ['$.a.b.c', dict(a=dict(b=dict(c='1'))), '1'],
                             ['$.a.0.c', dict(a=[dict(c=False)]), False],
                             ['$.a.c', dict(a=[dict(c=False)]), [False]]
                         ])
def test_extract_field(field, obj, val):
    from parser import extract_path_value
    assert extract_path_value(obj=obj, path=field) == val


DEFAULT = 'test'

@pytest.mark.parametrize(["field", 'obj', 'val', 'default'],
                         [
                             ['$.a.b.d', dict(a=dict(b=dict(c='1'))), DEFAULT, DEFAULT],
                             ['$.a.0.d', dict(a=[dict(c=False)]), DEFAULT, DEFAULT],
                             ['$.a.d', dict(a=[dict(c=False)]), [DEFAULT], DEFAULT]
                         ])
def test_extract_default_field(field, obj, val, default):
    from parser import extract_path_value
    assert extract_path_value(obj=obj, path=field, default=default) == val
