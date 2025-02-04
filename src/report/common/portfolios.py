from collections import defaultdict

from report.utils import generate_section
from utils import multi_extract_object_reader


def process_portfolios(directory, extract_mapping, server_id_mapping):
    portfolios = defaultdict(dict)
    for url, portfolio in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getPortfolioDetails'):
        server_id = server_id_mapping[url]
        portfolios[server_id][portfolio['key']] = dict(
            name=portfolio['name'],
            server_id=server_id,
            projects=set(),
            project_count=0,
            selection=extract_selection_modes(portfolio=portfolio),
            children="Yes" if portfolio.get('subViews') else "No",
        )
    for url, project in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getPortfolioProjects'):
        server_id = server_id_mapping[url]
        if project['portfolioKey'] not in portfolios[server_id].keys():
            continue
        portfolios[server_id][project['portfolioKey']]['projects'].add(project['refKey'])
        portfolios[server_id][project['portfolioKey']]['project_count'] = len(portfolios[server_id][project['portfolioKey']]['projects'])
    return [portfolio for server_id, p in portfolios.items() for portfolio in p.values()]


def extract_selection_modes(portfolio):
    selection_modes = set()
    if portfolio.get('selectionMode'):
        selection_modes.add(portfolio['selectionMode'])
    for child in portfolio.get('subViews', list()):
        selection_modes = selection_modes.union(extract_selection_modes(portfolio=child))
    return selection_modes


def generate_portfolio_markdown(directory, extract_mapping, server_id_mapping):
    portfolios = process_portfolios(directory=directory, extract_mapping=extract_mapping,
                                    server_id_mapping=server_id_mapping)
    active_portfolios = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Portfolio Name': 'name', 'Project selection type': 'selection',
                         'Contains Nested Portfolios': 'children', '# of Projects': 'project_count'},
        rows=portfolios, title='Active Portfolios', level=3, sort_by_lambda=lambda x: x['project_count'],
        sort_order='desc', filter_lambda=lambda x: x['project_count'] > 0
    )

    inactive_portfolios = generate_section(
        headers_mapping={'Server ID': 'server_id', 'Portfolio Name': 'name', 'Project selection type': 'selection'},
        rows=portfolios, title='Inactive Portfolios', level=3, sort_by_lambda=lambda x: x['name'],
        sort_order='asc', filter_lambda=lambda x: x['project_count'] == 0
    )
    return active_portfolios, inactive_portfolios