from report.utils import generate_section
from utils import multi_extract_object_reader
from collections import defaultdict
from datetime import datetime, UTC, timedelta
def process_tokens(directory, extract_mapping, server_id_mapping):
    tokens = defaultdict(lambda: dict(
        total_tokens=0,
        expired_tokens=0,
        recent_tokens=0,
        users=set(),
        user_count=0
    ))
    for url, token in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUserTokens'):
        server_id = server_id_mapping[url]
        tokens[server_id]['server_id'] = server_id
        if 'sonarlint' in token['name'].lower() or token['type'] != 'USER_TOKEN':
            continue
        tokens[server_id]['total_tokens'] += 1
        if token.get('isExpired'):
            tokens[server_id]['expired_tokens'] += 1
        if token.get('lastConnectionDate') and datetime.strptime(token['lastConnectionDate'], '%Y-%m-%dT%H:%M:%S%z') > datetime.now(tz=UTC) - timedelta(days=30):
            tokens[server_id]['recent_tokens'] += 1
        tokens[server_id]['active_tokens'] = tokens[server_id]['total_tokens'] - tokens[server_id]['expired_tokens']
        tokens[server_id]['users'].add(token['login'])
        tokens[server_id]['user_count'] = len(tokens[server_id]['users'])
    return tokens

def generate_token_markdown(directory, extract_mapping, server_id_mapping):
    tokens = process_tokens(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)

    return generate_section(
        title='Tokens',
        headers_mapping={"Server ID": "server_id", "Total Tokens": "total_tokens", "Active Tokens": "active_tokens",
                         "Recently Used Tokens": "recent_tokens", "Users": "user_count"},
        rows=tokens.values(),
    )
