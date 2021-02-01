# -*- coding: utf-8 -*-

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

import datetime

from . import utils
from .enums import MembershipScreeningFormFieldType, try_enum

__all__ = (
    'MembershipScreeningForm',
    'PartialMembershipScreeningForm',
    'MembershipScreeningFormField',
    'ServerRules'
)

EmptyMembershipScreeningFormField = utils._Empty('MembershipScreeningFormField.Empty')

class MembershipScreeningForm:
    """Represents a guild membership screening form from Discord.
    
    .. versionadded:: 1.7

    Attributes
    -----------
    guild: :class:`Guild`
        The :class:`Guild` that the membership screening form is for.
    version: :class:`datetime.datetime`
        When the membership screening form was set.
    description: Optional[:class:`str`]
        A short description of the guild seen by members when they join.
        Could be None
    fields: List[:class:`MembershipScreeningFormField`]
        The list of fields in the membership screening form.
    """

    def __init__(self, guild, data):
        self._state = guild._state
        self.guild = guild
        self._from_data(data)

    def _from_data(self, data):
        self.version = datetime.datetime.strptime(data['version'], '%Y-%m-%dT%H:%M:%S.%f+00:00')
        self.description = data.get('description')
        self.fields = [MembershipScreeningFormField.from_dict(f) for f in data['form_fields']]
    
    @property
    def enabled(self):
        """:class:`bool` Returns whether the guild has enabled membership screening."""
        return 'MEMBER_VERIFICATION_GATE_ENABLED' in self.guild.features

    async def update(self, **fields):
        """|coro|

        Updates the membership screening form.

        Raises
        ------
        HTTPException
            Editing the membership screening form.
        Forbidden
            You do not have permissions to update the guild's membership screening form.

        Parameters
        -----------
        enabled: Optional[:class:`bool`]
            Sets whether to enable or disable membership screening.
        fields: Optional[List[:class:`MembershipScreeningFormField`]]
            The new form fields.
        description: Optional[:class:`str`]
            The new server description to show in the membership screening form.
        """
        try:
            form_fields = fields['fields']
        except KeyError:
            pass
        else:
            fields['form_fields'] = [str(f.to_dict()) for f in form_fields]

        if fields:
            data = await self._state.http.update_member_verification(self.guild.id, **fields)
            self._from_data(data)

class PartialMembershipScreeningForm:

    __slots__ = ('guild', '_state')

    def __init__(self, *, guild):
        self.guild = guild
        self._state = guild._state

    def __repr__(self):
        return '<PartialMembershipScreeningForm guild={0.guild}>'.format(self)

    @property
    def enabled(self):
        """:class:`bool` Returns whether the guild has enabled membership screening."""
        return 'MEMBER_VERIFICATION_GATE_ENABLED' in self.guild.features

    async def fetch(self):
        """|coro|

        Fetches the partial membership screening form to a full :class:`MembershipScreeningForm`

        Raises
        -------
        HTTPException
            Retrieving the membership screening form failed.

        Returns
        --------
        :class:`MembershipScreeningForm`
            The full membership screening form.
        """
        data = await self._state.http.get_member_verification(self.guild.id)
        return MembershipScreeningForm(self.guild, data)

    async def update(self, **fields):
        """|coro|

        Updates the membership screening form.

        Parameters
        -----------
        enabled: Optional[:class:`bool`]
            Sets whether to enable or disable membership screening.
        fields: Optional[List[:class:`MembershipScreeningFormField`]]
            The new form fields.
        description: Optional[:class:`str`]
            The new server description to show in the membership screening form.

        Raises
        ------
        HTTPException
            Editing the membership screening form.
        Forbidden
            You do not have permissions to update the guild's membership screening form.

        Returns
        --------
        Optional[:class:`MembershipScreeningForm`]
            The membership screening form that was edited.
        """
        try:
            form_fields = fields['fields']
        except KeyError:
            pass
        else:
            fields['form_fields'] = [str(f.to_dict()) for f in form_fields]

        if fields:
            data = await self._state.http.update_member_verification(self.guild.id, **fields)
            return MembershipScreeningForm(self.guild, data)

class MembershipScreeningFormField:
    """Represents a Discord membership screening form field.

    Attributes
    -----------
    type: Union[:class:`MembershipScreeningFormFieldType`, :class:`str`]
        The type of this field.
        This must be set during initialisation.
    label: :class:`str`
        The label of this field.
        This must be set during initialisation.
    values: List[:class:`str`]
        The list of field values.
        This can be set during initialisation.
    required: :class:`bool`
        Sets whether this field is required or not.
        This must be set during initialisation.
    Empty
        A special sentinel value used by this class to denote that
        the value or attribute is empty.
    """

    __slots__ = ('type', 'label', '_values', 'required')

    Empty = EmptyMembershipScreeningFormField

    def __init__(self, *, type, label, required, **kwargs):
        self.type = try_enum(MembershipScreeningFormFieldType, type)
        self.label = label
        self.required = required

        try:
            values = kwargs['values']
        except KeyError:
            pass
        else:
            self.values = values

    @classmethod
    def from_dict(cls, data):
        """Converts a :class:`dict` to a :class:`MembershipScreeningFormField` provided 
        it is in the format that Discord expects it to be in.

        You can find out about this format in the `official Discord documentation`__.

        .. _DiscordDocs: https://discord.com/developers/docs/resources/guild#membership-screening-object-membership-screening-field-structure

        __ DiscordDocs_

        Parameters
        -----------
        data: :class:`dict`
            The dictionary to convert into a membership screening field.
        """
        cls, field_type = _membership_screening_field_factory(data['field_type'])

        # we are bypassing __init__ here since it doesn't apply here
        self = cls.__new__(cls)

        # fill fields
        self.type = field_type

        for attr in ('label', 'required'):
            setattr(self, attr, data[attr])

        try:
            self._values = data['values']
        except KeyError:
            pass

        return self

    def copy(self):
        """Returns a shallow copy of the membership screening form field."""
        return MembershipScreeningFormField.from_dict(self.to_dict())

    @property
    def values(self):
        return getattr(self, '_values', EmptyMembershipScreeningFormField)

    @values.setter
    def values(self, value):
        if isinstance(value, (list, utils._Empty)):
            if isinstance(value, list):
                if not all(isinstance(item, str) for item in value):
                    raise TypeError('Expected List[str] or MembershipScreeningFormField.Empty but recieved List[%s] instead' % item.__class__.__name__)
            self._values = value
            return
                
        raise TypeError('Expected List[str] or MembershipScreeningFormField.Empty but recieved %s instead' % value.__class__.__name__)

    def to_dict(self):
        """Converts this membership screening form field object into a dict."""

        # add in the raw data into the dict
        result = {
            key[1:]: getattr(self, key)
            for key in self.__slots__
            if key[0] == '_' and hasattr(self, key)
        }

        # add in the non raw attribute ones
        if isinstance(self.type, MembershipScreeningFormFieldType):
            result['field_type'] = self.type.value
        else:
            result['field_type'] = self.type
        result['label'] = self.label
        result['required'] = self.required

        return result

class ServerRules(MembershipScreeningFormField):
    """Represents a server rules Discord membership screening form field.

    Attributes
    -----------
    type: Union[:class:`MembershipScreeningFormFieldType`, :class:`str`]
        The type of this field.
        This must be set during initialisation.
    label: :class:`str`
        The label of this field.
        This must be set during initialisation.
    values: List[:class:`str`]
        The list of server rules.
        This can be set during initialisation.
    required: :class:`bool`
        Sets whether this field is required or not.
        This must be set during initialisation.
    Empty
        A special sentinel value used by this class to denote that
        the value or attribute is empty.
    """
    ...

def _membership_screening_field_factory(field_type):
    value = try_enum(MembershipScreeningFormFieldType, field_type)
    if value is MembershipScreeningFormFieldType.server_rules:
        return ServerRules, value
    else:
        return MembershipScreeningFormField, value
