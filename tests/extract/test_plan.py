from extract.plan import get_available_entity_configs

def test_multiple_entity_configs():
    r = get_available_entity_configs(server_version=10.6, edition='enterprise')
    assert 'labeled_issues' in r.keys()

def test_server_version_filters_entity_configs():
    r = get_available_entity_configs(server_version=0.1, edition='enterprise')
    assert not r

def test_available_configs(edition, version):
    r = get_available_entity_configs(edition=edition, server_version=float(version))
    assert r

