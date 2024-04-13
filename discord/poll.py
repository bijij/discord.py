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

from typing import TYPE_CHECKING, AsyncIterator, Optional, Union, List

from . import utils
from .enums import PollLayoutType, try_enum
from .partial_emoji import PartialEmoji
from .member import Member
from .user import User
from .object import Object

if TYPE_CHECKING:
    from .types.poll import (
        PollAnswer as PollAnswerPayload,
        PollAnswerCount as PollAnswerCountPayload,
        Poll as PollPayload,
    )

    from .abc import Snowflake
    from .message import Message

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
    text: Optional[:class:`str`]
        The text of the answer.
    emoji: Optional[:class:`PartialEmoji`]
        The emoji of the answer.
    vote_count: :class:`int`
        The number of votes the answer has.
    me: :class:`bool`
        Whether the current user has voted for this answer.
    """

    __slots__ = (
        'id',
        'text',
        'emoji',
        'vote_count',
        'me',
        '_poll',
    )

    def __init__(
        self,
        poll: Poll,
        data: PollAnswerPayload,
        count: Optional[PollAnswerCountPayload],
    ) -> None:
        self.id: int = data['answer_id']
        self.text: str | None = data['poll_media'].get('text')
        self.emoji: Optional[PartialEmoji]
        try:
            self.emoji = PartialEmoji.from_dict(data['emoji'])  # type: ignore
        except KeyError:
            self.emoji = None
        self.vote_count: int = count['count'] if count is not None else 0
        self.me: bool = count['me_voted'] if count is not None else False
        self._poll: Poll = poll

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
            limit = self.vote_count

        while limit > 0:
            retrieve = min(limit, 100)

            after_id = after.id if after else None

            message = self._poll.message
            state = message._state
            guild = message.guild

            data = await state.http.get_answer_voters(message.channel.id, message.id, self.id, retrieve, after=after_id)

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
        self.vote_count += 1
        if me:
            self.me = True

    def _remove_vote(self, me: bool) -> None:
        self.vote_count -= 1
        if me:
            self.me = False


class Poll:
    """Represents a poll.

    .. versionadded:: 2.4

    Attributes
    -----------
    message: :class:`Message`
        The message that the poll is attached to.
    question: :class:`str`
        The question the poll is asking.
    answers: List[:class:`PollAnswer`]
        The list of answers to the poll.
    expires_at: :class:`datetime.datetime`
        The time when the poll expires.
    is_final: :class:`bool`
        Whether the poll is finished.
    allows_multiple_answers: :class:`bool`
        Whether the poll allows multiple answers.
    layout: :class:`PollLayoutType`
        The layout type of the poll.
    """

    __slots__ = (
        'message',
        'question',
        'answers',
        'expires_at',
        'is_final',
        'allows_multiple_answers',
        'layout',
        '_state',
    )

    def __init__(self, *, message: Message, data: PollPayload) -> None:
        answer_counts = {answer['id']: answer for answer in data['results']['answer_counts']}

        self.message: Message = message

        self.question: str = data['question']['text']
        self.answers: List[PollAnswer] = [
            PollAnswer(self, answer, answer_counts.get(answer['answer_id'])) for answer in data['answers']
        ]  # Should this be a dict?
        self.expires_at = datetime.datetime.fromisoformat(data['expiry'])
        self.is_final: bool = data['results']['is_finalized']
        self.allows_multiple_answers = data['allow_multiselect']
        self.layout = try_enum(PollLayoutType, data['layout_type'])

    async def stop(self) -> None:
        """|coro|

        Stops the poll, preventing further votes from being cast.

        Raises
        -------
        Forbidden
            You do not have the permissions to stop the poll.
        HTTPException
            Stopping the poll failed.
        """
        await self.message._state.http.expire_poll(self.message.channel.id, self.message.id)
