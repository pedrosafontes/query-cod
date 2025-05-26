import pytest
from queries.services.sql.parser import parse_sql
from queries.services.sql.transpiler.normaliser import SQLQueryNormaliser
from queries.services.types import RelationalSchema

from .schemas import movies_schema, schema


@pytest.mark.parametrize(
    'query,expected,schema',
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
            WHERE EXISTS (SELECT MovieStar.name
                          FROM MovieStar
                          WHERE MovieStar.birthdate = 1960 AND StarsIn.starName = MovieStar.name)
            """,
            movies_schema,
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
            WHERE NOT EXISTS (SELECT MovieStar.name
                              FROM MovieStar
                              WHERE MovieStar.birthdate = 1960 AND StarsIn.starName = MovieStar.name)
            """,
            movies_schema,
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
                             WHERE MovieExec.netWorth < E.netWorth)
            """,
            movies_schema,
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
                         WHERE MovieExec.netWorth >= E.netWorth)
            """,
            movies_schema,
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
            WHERE EXISTS (SELECT SUM(R.B) FROM R
                          GROUP BY R.A
                          HAVING S.C = SUM(R.B))
            """,
            schema,
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
            WHERE EXISTS (SELECT SUM(R.B) FROM R
                          GROUP BY R.A
                          HAVING S.C > SUM(R.B))
            """,
            schema,
        ),
    ],
)
def test_subquery_normalisation(
    query: str,
    expected: str,
    schema: RelationalSchema,
) -> None:
    test_query = parse_sql(query)
    expected_query = parse_sql(expected)

    normalised_query = SQLQueryNormaliser.normalise_subqueries(test_query, schema)
    print(normalised_query.sql(pretty=True))

    assert normalised_query == expected_query


@pytest.mark.parametrize(
    'query,expected',
    [
        # Unaltered when there are no subqueries
        (
            """
            SELECT *
            FROM R
            WHERE A OR B
            """,
            """
            SELECT *
            FROM R
            WHERE A OR B
            """,
        ),
        (
            """
            SELECT *
            FROM R
            WHERE A > (SELECT C FROM S)
            OR B < (SELECT D FROM S)
            """,
            """
            SELECT *
            FROM R
            WHERE A > (SELECT C FROM S)
            UNION
            SELECT *
            FROM R
            WHERE B < (SELECT D FROM S)
            """,
        ),
    ],
)
def test_condition_normalisation(
    query: str,
    expected: str,
) -> None:
    test_query = parse_sql(query)
    expected_query = parse_sql(expected)

    normalised_query = SQLQueryNormaliser.normalise_conditions(test_query)
    print(normalised_query.sql(pretty=True))

    assert normalised_query == expected_query


@pytest.mark.parametrize(
    'query,expected',
    [
        (
            """
            SELECT * FROM R, R
            """,
            """
            SELECT * FROM R, R AS R1
            """,
        ),
        (
            """
            SELECT * FROM R, (SELECT R.A FROM R) AS R1
            """,
            """
            SELECT * FROM R, (SELECT R2.A FROM R AS R2) AS R1
            """,
        ),
    ],
)
def test_table_aliasing(
    query: str,
    expected: str,
) -> None:
    test_query = parse_sql(query)
    expected_query = parse_sql(expected)

    normalised_query = SQLQueryNormaliser.alias_tables(test_query)
    print(normalised_query.sql(pretty=True))

    assert normalised_query.sql() == expected_query.sql()
