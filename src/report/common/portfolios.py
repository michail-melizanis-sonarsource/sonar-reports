from collections import defaultdict

from utils import multi_extract_object_reader

ACTIVE_TEMPLATE = """
### Active Portfolios
| Server ID | Portfolio Name | Project selection type | Contains Nested Portfolios | # of Projects | 
|:----------|:---------------|:-----------------------|:---------------------------|:---------------|
{active_portfolios}
"""

INACTIVE_TEMPLATE = """
### Inactive Portfolios
| Server ID | Portfolio Name | Project selection type | 
|:----------|:---------------|:-----------------------|
{inactive_portfolios}
"""


def process_portfolios(directory, extract_mapping, server_id_mapping):
    portfolios = defaultdict(dict)
    for url, portfolio in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                      key='getPortfolioDetails'):
        server_id = server_id_mapping[url]
        portfolios[server_id][portfolio['key']] = dict(
            name=portfolio['name'],
            server_id=server_id,
            projects=set(),
            selection=extract_selection_modes(portfolio=portfolio),
            children="Yes" if portfolio.get('subViews') else "No",
        )
    for url, project in multi_extract_object_reader(directory=directory, mapping=extract_mapping,
                                                    key='getPortfolioProjects'):
        server_id = server_id_mapping[url]
        if project['portfolioKey'] not in portfolios[server_id].keys():
            continue
        portfolios[server_id][project['portfolioKey']]['projects'].add(project['key'])
    return [portfolio for server_id, p in portfolios.items() for portfolio in p.values()]


def extract_selection_modes(portfolio):
    selection_modes = set()
    if portfolio.get('selectionMode'):
        selection_modes.add(portfolio['selectionMode'])
    for child in portfolio.get('subViews', list()):
        selection_modes = selection_modes.union(extract_selection_modes(portfolio=child))
    return selection_modes

def format_active_portfolios(portfolios):
    return "\n".join(
        ["| {server_id} | {name} | {selection} | {children} | {project_count} |".format(
            server_id=portfolio['server_id'],
            name=portfolio['name'],
            selection=", ".join(portfolio['selection']),
            children=portfolio['children'],
            project_count=len(portfolio['projects'])
        ) for portfolio in portfolios if len(portfolio['projects']) > 0])

def format_inactive_portfolios(portfolios):
    return "\n".join(
        ["| {server_id} | {name} | {selection} |".format(
            server_id=portfolio['server_id'],
            name=portfolio['name'],
            selection=", ".join(portfolio['selection'])
        ) for portfolio in portfolios if len(portfolio['projects']) == 0]
    )

def generate_portfolio_markdown(directory, extract_mapping, server_id_mapping):
    portfolios = process_portfolios(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    active_portfolios = format_active_portfolios(portfolios=portfolios)
    inactive_portfolios = format_inactive_portfolios(portfolios=portfolios)
    return ACTIVE_TEMPLATE.format(active_portfolios=active_portfolios), INACTIVE_TEMPLATE.format(inactive_portfolios=inactive_portfolios)
