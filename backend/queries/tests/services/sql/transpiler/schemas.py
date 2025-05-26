from query_cod.types import DataType


movies_schema = {
    'Movie': {
        'title': DataType.VARCHAR,
        'year': DataType.INTEGER,
        'length': DataType.INTEGER,
        'genre': DataType.VARCHAR,
        'studioName': DataType.VARCHAR,
        'producerC#': DataType.INTEGER,
    },
    'MovieStar': {
        'name': DataType.VARCHAR,
        'address': DataType.VARCHAR,
        'gender': DataType.CHAR,
        'birthdate': DataType.DATE,
    },
    'StarsIn': {
        'movieTitle': DataType.VARCHAR,
        'movieYear': DataType.INTEGER,
        'starName': DataType.VARCHAR,
    },
    'MovieExec': {
        'name': DataType.VARCHAR,
        'address': DataType.VARCHAR,
        'CERT#': DataType.INTEGER,
        'netWorth': DataType.INTEGER,
    },
    'Studio': {
        'name': DataType.VARCHAR,
        'address': DataType.VARCHAR,
        'presC#': DataType.INTEGER,
    },
}

schema = {
    'R': {
        'A': DataType.INTEGER,
        'B': DataType.INTEGER,
    },
    'S': {
        'C': DataType.INTEGER,
    },
}
