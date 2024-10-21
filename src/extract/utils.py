def configure_client_cert(key_file_path: str, pem_file_path: str, cert_password: str) -> tuple | None:
    cert = tuple([i for i in [pem_file_path, key_file_path, cert_password] if i is not None])
    return cert if cert else None


def generate_auth_headers(token, server_version):
    from base64 import b64encode
    headers = dict()
    if server_version >= 10:
        headers['Authorization'] = f"Bearer {token}"
    else:
        encoded_auth = b64encode((token + ':').encode('utf-8')).decode('utf-8')
        headers['Authorization'] = f"Basic {encoded_auth}"
    return headers


def get_server_details(url, cert, token, timeout):
    from httpx import Client
    edition_mapper = {
        "Data": "datacenter",
        "Developer": "developer",
        "Enterprise": "enterprise",
        "Community": "community"
    }
    edition = None
    sync_client = Client(base_url=url, cert=cert, timeout=timeout)
    server_version_resp = sync_client.get("/api/server/version")
    server_version = float('.'.join(server_version_resp.text.split(".")[:2]))
    headers = generate_auth_headers(token=token, server_version=server_version)
    server_details_resp = sync_client.get("/api/system/info", headers=headers)
    for k, v in edition_mapper.items():
        if k.lower() in server_details_resp.json()['System']['Edition'].lower():
            edition = v
            break
    return server_version, edition
