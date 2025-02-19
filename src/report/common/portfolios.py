from collections import defaultdict

from parser import extract_path_value
from report.utils import generate_section
from utils import multi_extract_object_reader


def process_portfolios(directory, extract_mapping, server_id_mapping):
    portfolios = defaultdict(lambda: defaultdict(lambda : dict(
        name=None,
        server_id=None,
        projects=set(),
        project_count=0,
        selection=set(),
        children=False
    )))
    for url, portfolio in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getPortfolioDetails'):
        server_id = server_id_mapping[url]
        portfolio_key = extract_path_value(obj=portfolio, path='$.key')
        children = extract_path_value(obj=portfolio, path='$.subViews')
        if not portfolio_key:
            continue
        portfolios[server_id][portfolio_key].update(
            name=portfolio['name'],
            server_id=server_id,
            selection=extract_selection_modes(portfolio=portfolio),
            children=True if children else False,
        )
    for url, project in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getPortfolioProjects'):
        server_id = server_id_mapping[url]
        portfolio_key = extract_path_value(obj=project, path='$.portfolioKey')
        project_key = extract_path_value(obj=project, path='$.refKey')
        if portfolio_key not in portfolios[server_id].keys():
            continue
        portfolio = portfolios[server_id][portfolio_key]
        portfolio['projects'].add(project_key)
        portfolio['project_count'] = len(portfolio['projects'])
    return [portfolio for server_id, p in portfolios.items() for portfolio in p.values()]


def extract_selection_modes(portfolio):
    selection_modes = set()
    selection_mode = extract_path_value(obj=portfolio, path='$.selectionMode')
    sub_views = extract_path_value(obj=portfolio, path='$.subViews', default=list())
    if selection_mode:
        selection_modes.add(selection_mode)
    for child in sub_views:
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