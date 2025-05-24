# import pytest
# from queries.services.ra.parser.ast import (
#     Attribute,
#     BinaryBooleanExpression,
#     BinaryBooleanOperator,
#     Comparison,
#     ComparisonOperator,
#     Projection,
#     RAQuery,
#     Relation,
#     Selection,
#     SetOperation,
#     SetOperator,
# )
# from queries.services.sql.parser import parse_sql
# from queries.services.sql.transpiler import SQLtoRATranspiler
# from queries.services.types import RelationalSchema
# from ra_sql_visualisation.types import DataType


# movies_schema = {
#     'Movie': {
#         'title': DataType.VARCHAR,
#         'year': DataType.INTEGER,
#         'length': DataType.INTEGER,
#         'genre': DataType.VARCHAR,
#         'studioName': DataType.VARCHAR,
#         'producerC#': DataType.INTEGER,
#     },
#     'MovieStar': {
#         'name': DataType.VARCHAR,
#         'address': DataType.VARCHAR,
#         'gender': DataType.CHAR,
#         'birthdate': DataType.DATE,
#     },
#     'StarsIn': {
#         'movieTitle': DataType.VARCHAR,
#         'movieYear': DataType.INTEGER,
#         'starName': DataType.VARCHAR,
#     },
#     'MovieExec': {
#         'name': DataType.VARCHAR,
#         'address': DataType.VARCHAR,
#         'CERT#': DataType.INTEGER,
#         'netWorth': DataType.INTEGER,
#     },
#     'Studio': {
#         'name': DataType.VARCHAR,
#         'address': DataType.VARCHAR,
#         'presC#': DataType.INTEGER,
#     },
# }

# schema = {
#     'R': {
#         'A': DataType.INTEGER,
#         'B': DataType.INTEGER,
#     },
#     'S': {
#         'C': DataType.INTEGER,
#     },
# }


# @pytest.mark.parametrize(
#     'sql_text,expected_ra,schema',
#     [
#         (
#             """
#             SELECT movieTitle
#             FROM StarsIn
#             WHERE EXISTS (SELECT name
#                           FROM MovieStar
#                           WHERE birthdate = 1960 AND name = starName)
#             """,
#             Projection(
#                 attributes=[
#                     Attribute('movieTitle'),
#                     Attribute('movieYear'),
#                     Attribute('starName'),
#                     Attribute('name'),
#                 ],
#                 subquery=Selection(
#                     condition=BinaryBooleanExpression(
#                         operator=BinaryBooleanOperator.AND,
#                         left=Comparison(
#                             left=Attribute('birthdate'),
#                             operator=ComparisonOperator.EQUAL,
#                             right=1960,
#                         ),
#                         right=Comparison(
#                             left=Attribute('name'),
#                             operator=ComparisonOperator.EQUAL,
#                             right=Attribute('starName'),
#                         ),
#                     ),
#                     subquery=SetOperation(
#                         left=Relation('StarsIn'),
#                         right=Relation('MovieStar'),
#                         operator=SetOperator.CARTESIAN,
#                     ),
#                 ),
#             ),
#             movies_schema,
#         ),
#         (
#             """
#             SELECT R1.A, R1.B
#             FROM R R1, S
#             WHERE EXISTS
#                 (SELECT R2.A, R2.B
#                  FROM R R2
#                  WHERE R2.A = R1.B AND EXISTS
#                     (SELECT R3.A, R3.B
#                      FROM R R3
#                      WHERE R3.A = R2.B AND R3.B = S.C))
#             """,
#             None,
#             schema,
#         ),
#     ],
# )
# def test_subquery_transpilation(
#     sql_text: str, expected_ra: RAQuery, schema: RelationalSchema
# ) -> None:
#     sql = parse_sql(sql_text)
#     # print(sql.to_s())
#     transpiled = SQLtoRATranspiler(schema).transpile(sql)
#     # print(transpiled)
#     # assert transpiled == expected_ra
