from .types import Schema


def format_schema(schema: Schema) -> str:
    lines: list[str] = []

    for table_name, columns in schema.items():
        lines.append(f'TABLE {table_name}')
        for col_name, col_info in columns.items():
            line = f"  {col_name} {col_info['type']}"

            if not col_info.get('nullable', True):
                line += ' NOT NULL'

            if col_info.get('primary_key', False):
                line += ' PRIMARY KEY'

            if ref := col_info.get('references'):
                line += f" REFERENCES {ref['table']}({ref['column']})"

            lines.append(line)

        lines.append('')  # add empty line between tables

    return '\n'.join(lines)
