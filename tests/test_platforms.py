# from jsonschema import validate
# import pytest
#
#
# @pytest.fixture(scope='session')
# def organization():
#     return 'test_org'
#
#
# @pytest.fixture(scope='session')
# def repo():
#     return 'test_repo'
#
#
# @pytest.fixture(scope='session')
# def platform_mod(platform):
#     from pipelines.platforms import get_platform_module
#     return get_platform_module(platform)
#
#
# @pytest.fixture(scope='session')
# def repository(platform_mod, organization, repo):
#     return platform_mod.generate_repository_string(repo_string=f'{organization}/{repo}')
#
#
# @pytest.fixture(scope='session')
# def branch_name():
#     return 'test-branch'
#
#
# @pytest.fixture(scope='session')
# def file_path():
#     return 'foo/bar.py'
#
#
# @pytest.fixture(scope='session')
# def secret():
#     return dict(name='test-secret', value='test-value')
#
#
# def test_create_org_secret(platform_mod, secret):
#     pass
#
#
# async def test_get_content(platform_mod, repository, token, file_path, branch_name):
#     output_schema = dict(
#         type='object',
#         required=['file_path'],
#         properties=dict(
#             file_path=dict(type='string'),
#             content=dict(type='string'),
#             sha=dict(type='string')
#         )
#     )
#     file_content, _ = await platform_mod.get_content(
#         token=token,
#         repository=repository,
#         file_path=file_path,
#         branch_name=branch_name
#     )
#     assert validate(instance=file_content, schema=output_schema) is None
#
#
# async def test_list_files(platform_mod):
#     pass
#
#
# async def test_create_pull_request(platform_mod):
#     pass
#
#
# async def test_get_default_branch(platform_mod):
#     pass
#
#
# async def test_create_branch(platform_mod):
#     pass
#
#
# def test_get_pipeline_files(platform_mod):
#     pass
