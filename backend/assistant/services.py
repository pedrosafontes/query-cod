from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from exercises.models.attempt import Attempt
from openai import OpenAI
from projects.models.query import Query
from queries.services.ra.parser import grammar

from .models import Message


client = OpenAI(api_key=settings.OPENAI_API_KEY)  # type: ignore[misc]


def build_assistant_prompt(query: Query | Attempt, user_message: str) -> str:
    lines = [
        f'You are a {query.language.upper()} instructor in the Query Cod educational app.',
        'The database schema is:',
        f'{query.database.schema}',
        "The student's query is:",
        f'{query.query}',
    ]

    if query.validation_errors:
        lines += [
            "The student's query has the following validation errors:",
            str(query.validation_errors),
        ]

    if query.language == 'sql':
        lines.append('The supported SQL dialect is SQL-92.')
    elif query.language == 'ra':
        lines += [
            'The Relational Algebra LaTeX grammar supported by the app is:',
            grammar,
        ]

    return '\n'.join(lines)


def assist(query: Query | Attempt, user_message: str) -> Message:
    # Save user message
    Message.objects.create(
        object_type=ContentType.objects.get_for_model(query),
        object_id=query.id,
        author=Message.Author.USER,
        content=user_message,
    )

    prompt = build_assistant_prompt(query, user_message)

    response = client.responses.create(
        model='gpt-4o',
        instructions=prompt,
        input=user_message,
    )

    return Message.objects.create(
        object_type=ContentType.objects.get_for_model(query),
        object_id=query.id,
        author=Message.Author.ASSISTANT,
        content=response.output_text,
    )
