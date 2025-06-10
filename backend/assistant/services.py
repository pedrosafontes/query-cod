from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from databases.utils import format_schema
from exercises.models.attempt import Attempt
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from projects.models.query import Query
from queries.models import Language
from queries.services.ra.parser import grammar

from .models import Message


client = OpenAI(api_key=settings.OPENAI_API_KEY)  # type: ignore[misc]


def build_system_prompt(query: Query | Attempt, system_prompt: str | None) -> str:
    lines = [
        f'You are an experienced {Language(query.language).label} educator.',
        'You help students learn by asking questions before giving answers.',
    ]

    if system_prompt:
        lines.append(system_prompt)

    lines += [
        '',
        'The database schema is:',
        f'{format_schema(query.database.schema)}',
        '',
    ]

    if query.language == 'sql':
        lines.append('The supported SQL dialect is SQL-92.')
    elif query.language == 'ra':
        lines += ['The Relational Algebra LaTeX grammar supported by the app is:', grammar, '']

    return '\n'.join(lines)


def build_user_prompt(query: Query | Attempt, user_message: str) -> str:
    lines = []
    last_message: Message | None = query.assistant_messages.last()
    if last_message is None or query.modified > last_message.created:
        lines = [
            'Current query:\n',
            f'{query.query}',
            '',
        ]

        if query.validation_errors:
            lines += [
                'Validation errors:',
                str(query.validation_errors),
                '',
            ]

    lines += [
        'User message:',
        f'{user_message}',
    ]

    return '\n'.join(lines)


def assist(query: Query | Attempt, user_message: str, system_prompt: str | None) -> Message:
    system_prompt = build_system_prompt(query, system_prompt)
    user_prompt = build_user_prompt(query, user_message)

    Message.objects.create(
        object_type=ContentType.objects.get_for_model(query),
        object_id=query.id,
        author=Message.Author.USER,
        content=user_message,
    )

    messages: list[ChatCompletionMessageParam] = [
        {'role': message.author, 'content': message.content}
        for message in query.assistant_messages.all()
    ]
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': system_prompt},
            *messages,
            {'role': 'user', 'content': user_prompt},
        ],
        temperature=0.5,
        max_completion_tokens=400,
    )
    content = response.choices[0].message.content

    return Message.objects.create(
        object_type=ContentType.objects.get_for_model(query),
        object_id=query.id,
        author=Message.Author.ASSISTANT,
        content=content,
    )
