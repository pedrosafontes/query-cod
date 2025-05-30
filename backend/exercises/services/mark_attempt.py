from queries.services.execution import execute_query

from ..models.attempt import Attempt
from ..models.feedback import Feedback


def mark_attempt(attempt: Attempt) -> Feedback:
    results = execute_query(attempt)
    is_correct = results == attempt.exercise.solution_data

    if is_correct:
        attempt.completed = True
        attempt.save()

    return {'correct': is_correct, 'results': results}
