from queries.services.execution import execute_query

from ..models.attempt import Attempt


def mark_attempt(attempt: Attempt) -> bool:
    sample_solution = Attempt(
        text=attempt.exercise.solution,
        exercise=attempt.exercise,
        user=attempt.user,
    )

    return execute_query(attempt) == execute_query(sample_solution)
