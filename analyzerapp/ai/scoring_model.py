# analyzerapp/ai/scoring_model.py

def calculate_score(comm, rel, conf):
    """
    Calculates average score based on 3 metrics:
    - Communication
    - Relevance
    - Confidence
    Returns a float score rounded to 2 decimals.
    """
    total = (comm + rel + conf) / 3.0
    return round(total, 2)
