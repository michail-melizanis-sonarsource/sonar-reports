from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader
from collections import defaultdict
from datetime import datetime, UTC, timedelta

def process_tokens(directory, extract_mapping, server_id_mapping):
    tokens = defaultdict(lambda: dict(
        server_id=None,
        total_tokens=0,
        expired_tokens=0,
        recent_tokens=0,
        users=set(),
        user_count=0
    ))
    for url, token in multi_extract_object_reader(directory=directory, mapping=extract_mapping, key='getUserTokens'):
        server_id = server_id_mapping[url]
        tokens[server_id]['server_id'] = server_id
        token_name = extract_path_value(obj=token, path='$.name')
        token_type = extract_path_value(obj=token, path='$.type')
        is_expired = extract_path_value(obj=token, path='$.isExpired', default=False)
        last_connection_date = extract_path_value(obj=token, path='$.lastConnectionDate')
        if not all([token_name, token_type]):
            continue
        if 'sonarlint' in token_name.lower() or token_type.upper() != 'USER_TOKEN':
            continue
        tokens[server_id]['total_tokens'] += 1
        if is_expired:
            tokens[server_id]['expired_tokens'] += 1
        if last_connection_date and datetime.strptime(last_connection_date, '%Y-%m-%dT%H:%M:%S%z') > datetime.now(tz=UTC) - timedelta(days=30):
            tokens[server_id]['recent_tokens'] += 1
        tokens[server_id]['active_tokens'] = tokens[server_id]['total_tokens'] - tokens[server_id]['expired_tokens']
        tokens[server_id]['users'].add(extract_path_value(obj=token, path='$.login'))
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
