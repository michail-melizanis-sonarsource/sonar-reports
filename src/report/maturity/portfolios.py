from report.common.portfolios import process_portfolios
from report.utils import generate_section


def generate_portfolio_summary_markdown(directory, extract_mapping, server_id_mapping):
    portfolios = process_portfolios(directory=directory, extract_mapping=extract_mapping, server_id_mapping=server_id_mapping)
    row = dict(
        portfolios=0,
        projects=set(),
        project_count=0
    )
    for portfolio in portfolios:
        row['portfolios'] += 1
        row['projects'] = row['projects'].union(portfolio['projects'])
        row['project_count'] = len(row['projects'])
    return generate_section(
        title='Portfolios',
        headers_mapping={
            "Portfolios Created": "portfolios",
            "Total Portfolio Projects": "project_count"
        },
        rows=[row],
    )
