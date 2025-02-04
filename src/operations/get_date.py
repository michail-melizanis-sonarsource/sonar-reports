from datetime import datetime, timedelta, UTC


def execute(days, output_format='%Y-%m-%d', **kwargs):
    return (datetime.now(tz=UTC) - timedelta(days=days)).strftime(output_format)
