from collections import defaultdict
from utils import multi_extract_object_reader
def generate_hash_id(data):
    """Generate a consistent uuid for a given input

    :return: a UUID4 formatted string
    """
    import json
    import uuid
    import hashlib
    hash_id = uuid.UUID(
        hashlib.md5(
            str(json.dumps(data, sort_keys=True)).encode('utf-8')
        ).hexdigest()
    )
    return str(hash_id)

def map_portfolios(export_directory, extract_mapping):
    portfolio_projects = defaultdict(set)
    portfolio_details = dict()
    for server_url, portfolio in multi_extract_object_reader(directory=export_directory, mapping=extract_mapping,
                                                             key='getPortfolioProjects'):
        unique_key = server_url + portfolio['portfolioKey']
        portfolio_projects[unique_key].add(portfolio['refKey'])
        portfolio_details[unique_key] = dict(
            source_portfolio_key=portfolio['portfolioKey'],
            name=portfolio['portfolioName'],
            server_url=server_url,
            description=portfolio.get('description',''),
        )
    unique_portfolios = dict()
    for key, projects in portfolio_projects.items():
        unique_key = generate_hash_id(list(projects))
        unique_portfolios[unique_key] = portfolio_details[key]
    return list(unique_portfolios.values())

