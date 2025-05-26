import pytest
from queries.services.ra.ast import (
    EQ,
    And,
    RAQuery,
    Relation,
    attribute,
)
from queries.services.sql.parser import parse_sql
from queries.services.sql.transpiler import SQLtoRATranspiler
from queries.services.types import RelationalSchema

from .schemas import movies_schema, schema


@pytest.mark.parametrize(
    'sql_text,expected_ra,schema',
    [
        (
            """
            SELECT movieTitle
            FROM StarsIn
            WHERE EXISTS (SELECT name
                          FROM MovieStar
                          WHERE birthdate = 1960 AND name = starName)
            """,
            Relation('MovieStar')
            .cartesian('StarsIn')
            .select(
                And(
                    EQ(attribute('birthdate'), 1960),
                    EQ(attribute('name'), attribute('starName')),
                )
            )
            .project(['movieTitle']),
            movies_schema,
        ),
        (
            """
            SELECT R1.A, R1.B
            FROM R R1, S
            WHERE EXISTS
                (SELECT R2.A, R2.B
                 FROM R R2
                 WHERE R2.A = R1.B AND EXISTS
                    (SELECT R3.A, R3.B
                     FROM R R3
                     WHERE R3.A = R2.B AND R3.B = S.C))
            """,
            (Relation('R').rename('R1'))
            .natural_join(
                (Relation('R').rename('R3'))
                .cartesian(Relation('R').rename('R2'))
                .cartesian(Relation('S'))
                .select(
                    And(
                        EQ(attribute('R3.A'), attribute('R2.B')),
                        EQ(attribute('R3.B'), attribute('S.C')),
                    )
                )
                .project(['R2.A', 'R2.B', 'S.C'])
            )
            .select(EQ(attribute('R2.A'), attribute('R1.B')))
            .project(['R1.A', 'R1.B']),
            schema,
        ),
    ],
)
def test_subquery_transpilation(
    sql_text: str, expected_ra: RAQuery, schema: RelationalSchema
) -> None:
    sql = parse_sql(sql_text)
    transpiled = SQLtoRATranspiler(schema).transpile(sql)
    print(transpiled)
    assert transpiled == expected_ra
