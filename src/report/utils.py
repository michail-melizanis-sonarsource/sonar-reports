from logs import log_event
from datetime import datetime

def generate_section(headers_mapping: dict[str, str], rows, level=3, title=None, description=None, sort_by_lambda=None, sort_order='asc', filter_lambda=None):
    """
    Generate a section for a report.

    :param headers_mapping: Mapping of headers to row keys.
    :param rows: List of rows for the table.
    :param level: Level of nesting.
    :param title: Title of the section.
    :param description: Description of the section.
    :param sort_by_lambda: Lambda to sort rows.
    :param sort_order: Sort Direction.
    :param filter_lambda: Lambda to filter rows.
    :return: Dictionary containing the section.
    """
    section = str()
    if title is not None:
        section += f"{'#' * level} {title}\n"
    if description is not None:
        section += f"{description}\n"
    section += "| " + " | ".join(headers_mapping.keys()) + " |\n"
    section += "|" + "|".join([':---' for _ in headers_mapping.keys()]) + "|\n"
    if filter_lambda is not None:
        rows = filter(filter_lambda, rows)
    if sort_by_lambda is not None:
        rows = sorted(rows, key=sort_by_lambda, reverse=sort_order == 'desc')
    for row in rows:
        section += "| " + " | ".join([format_value(value=row.get(val)) for val in headers_mapping.values()]) + " |\n"

        missing_fields = [val for val in headers_mapping.values() if val not in row]
        if missing_fields:
            log_event(level='warning', status='anomalous', process_type='report', payload={'row': str(row), "fields":missing_fields, "title": title},
                      logger_name='default')
    return section

def format_value(value):
    val = value
    if isinstance(value, int):
        val =  f"{value:,}"
    elif isinstance(value, float):
        val= f"{value:,.2f}"
    elif isinstance(value, bool):
        val= 'Yes' if value else 'No'
    elif isinstance(value, datetime):
        val = value.strftime('%Y-%m-%d')
    elif isinstance(value, list) or isinstance(value, set):
        val = ', '.join(value)
    elif value is None:
        val = ''
    return str(val)