from report.utils import generate_section


def generate_coverage_markdown(measures):
    row = dict(
        lines_to_cover=0,
        new_lines_to_cover=0,
        covered_lines=0,
        uncovered_lines=0,
        new_covered_lines=0,
        new_uncovered_lines=0,
    )
    for server_projects in measures.values():
        for project_measures in server_projects.values():
            for metric, measure in project_measures.items():
                if metric in row.keys():
                    row[metric] += int(measure)
    if row['lines_to_cover'] > 0:
        row['coverage'] = (row['lines_to_cover'] - row['uncovered_lines']) / row['lines_to_cover'] * 100
        row['covered_lines'] = row['lines_to_cover'] - row['uncovered_lines']
    if row['new_lines_to_cover'] > 0:
        row['new_coverage'] = (row['new_lines_to_cover'] - row['new_uncovered_lines']) / row['new_lines_to_cover'] * 100
        row['new_covered_lines'] = row['new_lines_to_cover'] - row['new_uncovered_lines']
    return generate_section(
        title="Code Coverage",
        headers_mapping={
            "Overall Total Lines to Cover": "lines_to_cover",
            "Covered Lines": "covered_lines",
            "Overall Coverage": "coverage",
            "New Code Lines to Cover": "new_lines_to_cover",
            "New Code Covered Lines": "new_covered_lines",
            "New Code Coverage": "new_coverage"
        },
        rows=[row]
    )
