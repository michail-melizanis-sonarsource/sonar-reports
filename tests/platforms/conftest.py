import pytest


@pytest.fixture(scope='session')
def organization():
    return 'test_org'


@pytest.fixture(scope='session')
def repo():
    return 'test_repo'


@pytest.fixture(scope='session')
def platform_mod(platform):
    from pipelines.platforms import get_platform_module
    return get_platform_module(platform)


@pytest.fixture(scope='session')
def repository(platform_mod, organization, repo):
    return platform_mod.generate_repository_string(repo_string=f'{organization}/{repo}')


@pytest.fixture(scope='session')
def branch_name():
    return 'test-branch'


@pytest.fixture(scope='session')
def file_path_test():
    return 'foo/bar.py'

@pytest.fixture(scope='session')
def get_content_schema_test():
    async def test_func():
        pass


@pytest.fixture(scope='session')
def create_pull_request_schema_test():
    pass

@pytest.fixture(scope='session')
def list_files_schema_test():
    pass

@pytest.fixture(scope='session')
def get_default_branch_schema_test():
    pass

@pytest.fixture(scope='session')
def create_branch_schema_test():
    pass

@pytest.fixture(scope='session')
def get_pipeline_files_schema_test():
    pass