from base64 import b64encode, b64decode
from nacl import encoding, public
from operations.http_request.base import safe_json_request
from urllib.parse import quote
from asyncio import gather
import os
from itertools import chain
DEFAULT_HOST = os.getenv('GITHUB_URL', 'https://api.github.com')


def get_available_pipelines():
    return ['github']


def generate_headers(token):
    return {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": "Bearer " + token,
        "X-GitHub-Api-Version": "2022-11-28"
    }


async def get_org_public_key(token, org_name, host=DEFAULT_HOST):
    url = f'/orgs/{org_name}/actions/secrets/public-key'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    return js['key_id'], js['key']


async def create_org_secret(token, organization, secret_name, secret_value, host=DEFAULT_HOST, **unused_kwargs):
    org_name = organization['sonarqube_org_key'].split('/')[-1]
    key_id, key = await get_org_public_key(token=token, org_name=org_name, host=host)
    url = f'/orgs/{org_name}/actions/secrets/{secret_name}'
    payload = {
        "org": org_name,
        "secret_name": secret_name,
        "encrypted_value": encrypt_secret(secret=secret_value, key=key),
        "key_id": key_id,
        "visibility": 'all',
    }
    unused, js = await safe_json_request(
        url=url, host=host, headers=generate_headers(token=token), method='PUT',
        json=payload, log_attributes=dict(
            secret_name=secret_name, org_name=org_name, key_id=key_id))
    return js


def encrypt_secret(secret, key):
    """Encrypt a Unicode string using the public key."""
    public_key = public.PublicKey(key.encode("utf-8"), encoding.Base64Encoder)
    sealed_box = public.SealedBox(public_key)
    encrypted = sealed_box.encrypt(secret.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


async def list_files(token, repository, file_path, branch_name, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/contents/{quote(file_path)}'
    _, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    files = []
    if isinstance(js, list):
        files= js
    return files


async def get_content(token, repository, file_path, branch_name, host=DEFAULT_HOST, extra_args=None, **unused_kwargs):
    url = f'/repos/{repository}/contents/{quote(file_path)}'
    _, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    file = dict(
        file_path=file_path,
        content='',
        sha=js.get('sha')
    )
    if js.get('content') is not None:
        file['content'] = b64decode(js['content']).decode('utf-8')
    elif js.get('download_url') is not None:
        _, sub_js = await safe_json_request(host=host, url=js['download_url'], headers=generate_headers(token=token),

                                            method='GET')
        file['content'] = sub_js['content']
    return file, extra_args


async def get_branch(token, repository, branch_name, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/branches/{branch_name}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    js['sha'] = js['commit']['sha']
    js['name'] = branch_name
    return js


async def get_commit(token, repository, commit_sha, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/git/commits/{commit_sha}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    return js


async def create_branch(token, repository, branch_name, base_branch_name, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/git/refs'
    base_branch = await get_branch(host=host, repository=repository, branch_name=base_branch_name, token=token)
    payload = {
        "ref": f"refs/heads/{branch_name}",
        "sha": base_branch['commit']['sha']
    }
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='POST',
                                         json=payload)
    branch = await get_branch(token=token, repository=repository, branch_name=branch_name, host=host)

    return branch


async def create_or_update_file(token, repository, message, branch_name, file_path, content: str, sha,
                                host=DEFAULT_HOST,
                                **unused_kwargs):
    url = f'/repos/{repository}/contents/{quote(file_path)}'
    payload = {
        "message": message,
        "content": b64encode(content.encode('utf-8')).decode('utf-8'),
        "branch": branch_name
    }
    if '.github/' in file_path:
        branch = await get_branch(token=token, repository=repository, branch_name=branch_name, host=host)
        payload['sha'] = branch['commit']['sha']
    if sha is not None:
        payload['sha'] = sha
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='PUT',
                                         json=payload,)
    return js


async def create_pull_request(token, repository, source_branch, target_branch, title, body, host=DEFAULT_HOST,
                              **unused_kwargs):
    url = f'/repos/{repository}/pulls'
    payload = {
        "title": title,
        "body": body,
        "head": source_branch,
        "base": target_branch
    }
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='POST',
                                         json=payload)
    return js


async def get_pull_request(token, repository, pr_name, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/pulls/{pr_name}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    return js


async def update_pull_request(token, repository, pr_name, body, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/pulls/{pr_name}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='PATCH',
                                         json=dict(body=body))
    return js


async def delete_branch(token, repository, branch_name, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}/git/refs/heads/{branch_name}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='DELETE')
    return js


async def get_default_branch(token, repository, host=DEFAULT_HOST, **unused_kwargs):
    url = f'/repos/{repository}'
    unused, js = await safe_json_request(url=url, host=host, headers=generate_headers(token=token), method='GET')
    return await get_branch(token=token, repository=repository, branch_name=js['default_branch'], host=host)


def generate_repository_string(repo_string, **_):
    return repo_string


async def get_pipeline_files(token, repository, branch_name, host=DEFAULT_HOST, **unused_kwargs):
    collections = await gather(*[
        list_files(token=token, repository=repository, file_path=path, branch_name=branch_name, host=host)
        for path in get_pipeline_file_paths()['folders']])
    return await gather(
        *[get_content(token=token, repository=repository, file_path=file['path'], branch_name=branch_name, host=host)
          for file in chain.from_iterable(collections)])


def get_pipeline_file_paths():
    return dict(
        files=[],
        folders=['.github/workflows']
    )


