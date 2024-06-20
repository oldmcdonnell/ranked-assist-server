# utils.py
from django.template.loader import render_to_string

def generate_vote_results(vote):
    # Your logic to calculate vote results
    results = {
        # Example structure
        'candidates': [
            {'description': 'Candidate 1', 'votes': 10},
            {'description': 'Candidate 2', 'votes': 15},
            # ...
        ],
        'winner': 'Candidate 2',
        'total_votes': 25,
        'rounds': 2,
    }

    # Render results to a template (e.g., HTML)
    html_content = render_to_string('vote_results_email.html', {'results': results})
    return html_content
