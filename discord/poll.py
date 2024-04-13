"""
The MIT License (MIT)

Copyright (c) 2015-present Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

import datetime

from typing import TYPE_CHECKING, AsyncIterator, Optional, Union, Sequence, List

from . import utils
from .enums import PollLayoutType, try_enum
from .member import Member
from .user import User
from .object import Object

if TYPE_CHECKING:
    from typing_extensions import Self

    from .types.emoji import PartialEmoji as PartialEmojiPayload
    from .types.poll import (
        PollAnswer as PollAnswerPayload,
        PollAnswerCount as PollAnswerCountPayload,
        Poll as PollPayload,
        PollCreateRequest as PollCreateRequestPayload,
        PollAnswerCreateRequest as PollAnswerCreateRequestPayload,
    )

    from .abc import Snowflake
    from .message import Message
    from .emoji import Emoji
    from .partial_emoji import PartialEmoji
    from .state import ConnectionState

MISSING = utils.MISSING


__all__ = (
    'PollAnswer',
    'Poll',
)


class PollAnswer:  # TODO: Do we like PollOption better?
    """Represents an answer to a poll.

    .. versionadded:: 2.4

    Attributes
    -----------
    id: :class:`int`
        The ID of the answer.

        .. Note::

            This identifier is provided by Discord, this value should be ignored on polls not attached to a message.

    text: :class:`str`
        The text of the answer.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji of the answer.
    vote_count: :class:`int`
        The number of votes the answer has.
    me: :class:`bool`
        Whether the current user has voted for this answer.
    """

    __slots__ = (
        'text',
        'emoji',
        '_poll',
        '_id',
        '_vote_count',
        '_me',
    )

    def __init__(
        self,
        *,
        text: str,
        emoji: Optional[Union[PartialEmoji, Emoji, str]],
    ) -> None:
        self.text: str = text
        self.emoji: Optional[Union[PartialEmoji, Emoji, str]] = emoji

        self._poll: Optional[Poll] = None
        self._id: Optional[int] = None
        self._vote_count: int = 0
        self._me: bool = False

    @property
    def poll(self) -> Poll | None:
        """:class:`Poll`: The poll this answer belongs to or ``None`` if the poll is not attached to a message."""
        return self._poll

    @property
    def id(self) -> int | None:
        """:class:`int`: The ID of the answer or ``None`` if the poll is not attached to a message."""
        return self._id

    @property
    def vote_count(self) -> int:
        """:class:`int`: The number of votes the answer has."""
        return self._vote_count

    @property
    def me(self) -> bool:
        """:class:`bool`: Whether the current user has voted for this answer."""
        return self._me

    @classmethod
    def _from_data(cls, data: PollAnswerPayload, *, state: ConnectionState) -> Self:
        emoji = None
        if 'emoji' in data['poll_media']:
            emoji = state.get_reaction_emoji(data['poll_media']['emoji'])

        return cls(text=data['poll_media'].get('text', ''), emoji=emoji)

    def _inject_state(self, poll: Poll, data: PollAnswerPayload, count: Optional[PollAnswerCountPayload]) -> None:
        self._poll = poll
        self._id = data['answer_id']
        self._vote_count = count['count'] if count is not None else 0
        self._me = count['me_voted'] if count is not None else False

        self.text = data['poll_media'].get('text', '')
        try:
            self.emoji = PartialEmoji.from_dict(data['emoji'])  # type: ignore
        except KeyError:
            self.emoji = None

    def to_dict(self) -> PollAnswerCreateRequestPayload:
        payload: PollAnswerCreateRequestPayload = {
            'poll_media': {'text': self.text},
        }

        emoji_payload: Optional[PartialEmojiPayload] = None

        if isinstance(self.emoji, str):
            emoji_payload = {"id": None, "name": self.emoji}
        elif self.emoji is not None:
            emoji_payload = {"id": self.emoji.id, "name": None}

        if emoji_payload is not None:
            payload['poll_media']['emoji'] = emoji_payload

        return payload

    async def voters(
        self,
        *,
        limit: Optional[int] = None,
        after: Snowflake = MISSING,
    ) -> AsyncIterator[Union[User, Member]]:
        """Returns an :term:`asynchronous iterator` representing the users that have voted for this answer.

        The ``after`` parameter must represent a user
        and meet the :class:`abc.Snowflake` abc.

        Examples
        --------

        Usage ::

            # I do not actually recommend doing this.
            async for user in answer.voters():
                await channel.send(f'{user} has voted for {answer.text}!')

        Flattening into a list: ::

            users = [user async for user in answer.voters()]

        Parameters
        -----------
        limit: Optional[:class:`int`]
            The maximum number of results to return.
            If not provided, returns all the users who
            voted for the answer.
        after: :class:`abc.Snowflake`
            For pagination, voters are sorted by user.

        Raises
        -------
        HTTPException
            Getting the voters for the answer failed.

        Yields
        -------
        Union[:class:`User`, :class:`Member`]
            The member (if retrievable) or the user that has voted
            for this answer. The case where it can be a :class:`Member` is
            in a guild message context. Sometimes it can be a :class:`User`
            if the member has left the guild.
        """
        if limit is None:
            limit = self._vote_count

        if self._id is None or self._poll is None or self._poll._message is None:
            raise RuntimeError('This poll answer is not attached to a message.')

        while limit > 0:
            retrieve = min(limit, 100)

            after_id = after.id if after else None

            message = self._poll._message
            state = message._state
            guild = message.guild

            data = await state.http.get_answer_voters(message.channel.id, message.id, self._id, retrieve, after=after_id)

            if data:
                limit -= len(data)
                after = Object(id=int(data[-1]['id']))
            else:
                break

            if guild is None or isinstance(guild, Object):
                for raw_user in reversed(data):
                    yield User(state=state, data=raw_user)

                continue

            for raw_user in reversed(data):
                member_id = int(raw_user['id'])
                member = guild.get_member(member_id)

                yield member or User(state=state, data=raw_user)

    def _add_vote(self, me: bool) -> None:
        self._vote_count += 1
        if me:
            self._me = True

    def _remove_vote(self, me: bool) -> None:
        self._vote_count -= 1
        if me:
            self._me = False


class Poll:
    """Represents a poll.

    .. versionadded:: 2.4

    Attributes
    -----------
    question: :class:`str`
        The question the poll is asking.
    answers: List[:class:`PollAnswer`]
        The list of answers to the poll.
    duration: Optional[:class:`datetime.timedelta`]
        The duration of the poll or ``None`` if the poll was retrieved from a message.
    allows_multiple_answers: :class:`bool`
        Whether the poll allows multiple answers.
    layout: :class:`PollLayoutType`
        The layout type of the poll.
    """

    __slots__ = (
        'question',
        'answers',
        'duration',
        'allows_multiple_answers',
        'layout',
        '_message',
        '_expires',
        '_final',
    )

    def __init__(
        self,
        *,
        question: str,
        answers: Sequence[Union[str, PollAnswer]],
        duration: datetime.timedelta,
        allows_mutiple_answers: bool,
        layout: PollLayoutType = PollLayoutType.default,
    ) -> None:
        self.question: str = question
        self.answers: List[PollAnswer] = []

        for answer in answers:
            if isinstance(answer, str):
                answer = PollAnswer(text=answer, emoji=None)

            if answer.poll is not None:
                raise ValueError('PollAnswer is already attached to a poll.')

            self.answers.append(answer)

        self.duration: datetime.timedelta | None = duration if duration is not MISSING else None
        self.allows_multiple_answers: bool = allows_mutiple_answers
        self.layout: PollLayoutType = layout

        self._message: Message | None = None
        self._expires: datetime.datetime | None = None
        self._final: bool = False

    @property
    def message(self) -> Message | None:
        """:class:`Message`: The message that the poll is attached to or ``None`` if this poll
        is not currently attached to a message."""
        return self._message

    @property
    def expires_at(self) -> datetime.datetime | None:
        """:class:`datetime.datetime`: The time when the poll expires or ``None`` if the poll
        is not attached to a message."""
        return self._expires

    @property
    def is_final(self) -> bool:
        """:class:`bool`: Whether the poll is finished."""
        return self._final

    @classmethod
    def _from_data(cls, data: PollPayload, *, message: Message) -> Self:
        answers = [PollAnswer._from_data(answer_data, state=message._state) for answer_data in data['answers']]
        layout = try_enum(PollLayoutType, data['layout_type'])
        return cls(
            question=data['question']['text'],
            answers=answers,
            allows_mutiple_answers=data['allow_multiselect'],
            duration=MISSING,
            layout=layout,
        )._inject_state(message, data)

    def _inject_state(self, message: Message, data: PollPayload) -> Self:
        self._message = message
        self._expires = datetime.datetime.fromisoformat(data['expiry'])
        self._final = data['results']['is_finalized']

        for answer, answer_data, count_data in zip(self.answers, data['answers'], data['results']['answer_counts']):
            answer._inject_state(self, answer_data, count_data)

        return self

    def to_dict(self) -> PollCreateRequestPayload:
        if self.duration is None:
            raise ValueError('Polls attached to messages cannot be created.')

        return {
            'question': {'text': self.question},
            'answers': [answer.to_dict() for answer in self.answers],
            'allow_multiselect': self.allows_multiple_answers,
            'layout_type': self.layout.value,
            'duration': int(self.duration.total_seconds() // 3600),
        }

    async def stop(self) -> None:
        """|coro|

        Stops the poll, preventing further votes from being cast.

        Raises
        -------
        RuntimeError
            This poll is not attached to a message.
        Forbidden
            You do not have the permissions to stop the poll.
        HTTPException
            Stopping the poll failed.
        """
        if self.message is None:
            raise RuntimeError('This poll is not attached to a message.')

        await self.message._state.http.expire_poll(self.message.channel.id, self.message.id)
