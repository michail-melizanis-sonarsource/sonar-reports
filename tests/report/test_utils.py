import pytest
from report.utils import generate_section


@pytest.fixture(scope='session')
def rows():
    return [
        {'name': 'John', 'age': 25},
        {'name': 'Jane', 'age': 30},
        {'name': 'Doe', 'age': 35}
    ]


def test_missing_field(rows):
    assert generate_section(
        headers_mapping={
            'Name': 'name',
            "Age": 'age',
            "Location": 'location'
        },
        rows=rows,
    )


def test_sort_section(rows):
    assert generate_section(
        headers_mapping={
            'Name': 'name',
            "Age": 'age',
        },
        rows=rows,
        sort_by_lambda=lambda x: x['age']
    )


def test_filter_section(rows):
    assert len(generate_section(
        headers_mapping={
            'Name': 'name',
            "Age": 'age',
        },
        rows=rows,
        filter_lambda=lambda x: x['age'] > 30
    ).splitlines()) == 3

