from extract.plan import get_available_entity_configs

def test_multiple_entity_configs():
    r = get_available_entity_configs(10.6)
    assert 'labeled_issues' in r.keys()

def test_server_version_filters_entity_configs():
    r = get_available_entity_configs(0.1)
    assert not r

