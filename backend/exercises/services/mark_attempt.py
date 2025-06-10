from databases.types import QueryResult
from queries.services.execution import execute_query

from ..models.attempt import Attempt
from ..models.feedback import Feedback


def _order_result(result: QueryResult) -> QueryResult:
    return {'columns': result['columns'], 'rows': sorted(result['rows'])}


def mark_attempt(attempt: Attempt) -> Feedback:
    attempt_results = execute_query(attempt)
    solution_results = attempt.exercise.solution_data

    if not attempt.exercise.is_order_significant:
        attempt_results = attempt_results and _order_result(attempt_results)
        solution_results = solution_results and _order_result(solution_results)

    is_correct = attempt_results == solution_results

    if is_correct:
        attempt.completed = True
        attempt.save()

    return {'correct': is_correct, 'results': attempt_results}
