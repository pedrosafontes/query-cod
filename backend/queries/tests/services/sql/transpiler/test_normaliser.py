import pytest
from queries.services.sql.parser import parse_sql
from queries.services.sql.transpiler.normaliser import SQLQueryNormaliser


@pytest.mark.parametrize(
    'query,expected',
    [
        # IN
        (
            """
            SELECT movieTitle FROM StarsIn
            WHERE starName IN (SELECT name
                               FROM MovieStar
                               WHERE birthdate = 1960)
            """,
            """
            SELECT movieTitle FROM StarsIn
            WHERE EXISTS (SELECT name
                          FROM MovieStar
                          WHERE birthdate = 1960 AND starName = name)
            """,
        ),
        # NOT IN
        (
            """
            SELECT movieTitle FROM StarsIn
            WHERE starName NOT IN (SELECT name
                                   FROM MovieStar
                                   WHERE birthdate = 1960)
            """,
            """
            SELECT movieTitle FROM StarsIn
            WHERE NOT EXISTS (SELECT name
                              FROM MovieStar
                              WHERE birthdate = 1960 AND starName = name)
            """,
        ),
        # ALL
        (
            """
            SELECT name FROM MovieExec
            WHERE netWorth >= ALL (SELECT E.netWorth
                                   FROM MovieExec E)
            """,
            """
            SELECT name FROM MovieExec
            WHERE NOT EXISTS(SELECT E.netWorth
                             FROM MovieExec E
                             WHERE netWorth < E.netWorth)
            """,
        ),
        # ANY
        (
            """
            SELECT name FROM MovieExec
            WHERE netWorth >= ANY (SELECT E.netWorth
                                   FROM MovieExec E)
            """,
            """
            SELECT name FROM MovieExec
            WHERE EXISTS(SELECT E.netWorth
                         FROM MovieExec E
                         WHERE netWorth >= E.netWorth)
            """,
        ),
        # IN - Grouped Subquery
        (
            """
            SELECT C FROM S
            WHERE C IN (SELECT SUM(B) FROM R
                        GROUP BY A)
            """,
            """
            SELECT C FROM S
            WHERE EXISTS (SELECT SUM(B) FROM R
                          GROUP BY A
                          HAVING C = SUM(B))
            """,
        ),
        # No quantifier
        (
            """
            SELECT C FROM S
            WHERE C > (SELECT SUM(B) FROM R
                       GROUP BY A)
            """,
            """
            SELECT C FROM S
            WHERE EXISTS (SELECT SUM(B) FROM R
                          GROUP BY A
                          HAVING C > SUM(B))
            """,
        ),
        # Subquery with set operation
        (
            """
            SELECT movieTitle FROM StarsIn
            WHERE starName IN (SELECT name
                               FROM MovieStar
                               WHERE birthdate = 1960
                               UNION
                               SELECT name
                               FROM MovieStar
                               WHERE birthdate = 1970)
            """,
            """
            SELECT movieTitle FROM StarsIn
            WHERE EXISTS (SELECT *
                          FROM (SELECT name
                                FROM MovieStar
                                WHERE birthdate = 1960
                                UNION
                                SELECT name
                                FROM MovieStar
                                WHERE birthdate = 1970) AS sub
                          WHERE starName = name)
            """,
        ),
    ],
)
def test_subquery_normalisation(
    query: str,
    expected: str,
) -> None:
    parsed_query = parse_sql(query)
    expected_query = parse_sql(expected)
    normalised_query = SQLQueryNormaliser().normalise(parsed_query)
    print(normalised_query.sql(pretty=True))

    assert normalised_query == expected_query
