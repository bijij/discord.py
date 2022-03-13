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

from typing import TYPE_CHECKING, List, Literal, Optional, TypedDict, Union

if TYPE_CHECKING:
    from .channel import ChannelType, PermissionOverwrite, PrivacyLevel, VideoQualityMode
    from .guild import DefaultMessageNotificationLevel, ExplicitContentFilterLevel, MFALevel, VerificationLevel
    from .integration import IntegrationExpireBehavior, PartialIntegration
    from .role import Role
    from .scheduled_event import EntityType, EventStatus, GuildScheduledEvent
    from .snowflake import Snowflake
    from .threads import Thread
    from .user import User
    from .webhook import Webhook

__all__ = (
    'AuditEntryInfo',
    'AuditLog',
    'AuditLogChange',
    'AuditLogEntry',
    'AuditLogEvent',
)


_GuildUpdate = Literal[1]
_ChannelCreate = Literal[10]
_ChannelUpdate = Literal[11]
_ChannelDelete = Literal[12]
_ChannelOverwriteCreate = Literal[13]
_ChannelOverwriteUpdate = Literal[14]
_ChannelOverwriteDelete = Literal[15]
_MemberKick = Literal[20]
_MemberPrune = Literal[21]
_MemberBanAdd = Literal[22]
_MemberBanRemove = Literal[23]
_MemberUpdate = Literal[24]
_MemberRoleUpdate = Literal[25]
_MemberMove = Literal[26]
_MemberDisconnect = Literal[27]
_BotAdd = Literal[28]
_RoleCreate = Literal[30]
_RoleUpdate = Literal[31]
_RoleDelete = Literal[32]
_InviteCreate = Literal[40]
_InviteUpdate = Literal[41]
_InviteDelete = Literal[42]
_WebhookCreate = Literal[50]
_WebhookUpdate = Literal[51]
_WebhookDelete = Literal[52]
_EmojiCreate = Literal[60]
_EmojiUpdate = Literal[61]
_EmojiDelete = Literal[62]
_MessageDelete = Literal[72]
_MessageBulkDelete = Literal[73]
_MessagePin = Literal[74]
_MessageUnpin = Literal[75]
_IntegrationCreate = Literal[80]
_IntegrationUpdate = Literal[81]
_IntegrationDelete = Literal[82]
_StageInstanceCreate = Literal[83]
_StageInstanceUpdate = Literal[84]
_StageInstanceDelete = Literal[85]
_StickerCreate = Literal[90]
_StickerUpdate = Literal[91]
_StickerDelete = Literal[92]
_GuildScheduledEventCreate = Literal[100]
_GuildScheduledEventUpdate = Literal[101]
_GuildScheduledEventDelete = Literal[102]
_ThreadCreate = Literal[110]
_ThreadUpdate = Literal[111]
_ThreadDelete = Literal[112]


AuditLogEvent = Union[
    _GuildUpdate,
    _ChannelCreate,
    _ChannelUpdate,
    _ChannelDelete,
    _ChannelOverwriteCreate,
    _ChannelOverwriteUpdate,
    _ChannelOverwriteDelete,
    _MemberKick,
    _MemberPrune,
    _MemberBanAdd,
    _MemberBanRemove,
    _MemberUpdate,
    _MemberRoleUpdate,
    _MemberMove,
    _MemberDisconnect,
    _BotAdd,
    _RoleCreate,
    _RoleUpdate,
    _RoleDelete,
    _InviteCreate,
    _InviteUpdate,
    _InviteDelete,
    _WebhookCreate,
    _WebhookUpdate,
    _WebhookDelete,
    _EmojiCreate,
    _EmojiUpdate,
    _EmojiDelete,
    _MessageDelete,
    _MessageBulkDelete,
    _MessagePin,
    _MessageUnpin,
    _IntegrationCreate,
    _IntegrationUpdate,
    _IntegrationDelete,
    _StageInstanceCreate,
    _StageInstanceUpdate,
    _StageInstanceDelete,
    _StickerCreate,
    _StickerUpdate,
    _StickerDelete,
    _GuildScheduledEventCreate,
    _GuildScheduledEventUpdate,
    _GuildScheduledEventDelete,
    _ThreadCreate,
    _ThreadUpdate,
    _ThreadDelete,
]


class _AuditLogChange_Str(TypedDict):
    key: Literal[
        'name',
        'description',
        'preferred_locale',
        'vanity_url_code',
        'topic',
        'code',
        'allow',
        'deny',
        'permissions',
        'tags',
        'unicode_emoji',
    ]
    new_value: str
    old_value: str


class _AuditLogChange_AssetHash(TypedDict):
    key: Literal['icon_hash', 'splash_hash', 'discovery_splash_hash', 'banner_hash', 'avatar_hash', 'asset']
    new_value: str
    old_value: str


class _AuditLogChange_Snowflake(TypedDict):
    key: Literal[
        'id',
        'owner_id',
        'afk_channel_id',
        'rules_channel_id',
        'public_updates_channel_id',
        'widget_channel_id',
        'system_channel_id',
        'application_id',
        'channel_id',
        'inviter_id',
        'guild_id',
    ]
    new_value: Snowflake
    old_value: Snowflake


class _AuditLogChange_Bool(TypedDict):
    key: Literal[
        'widget_enabled',
        'nsfw',
        'hoist',
        'mentionable',
        'temporary',
        'deaf',
        'mute',
        'nick',
        'enabled_emoticons',
        'region',
        'rtc_region',
        'available',
        'archived',
        'locked',
    ]
    new_value: bool
    old_value: bool


class _AuditLogChange_Int(TypedDict):
    key: Literal[
        'afk_timeout',
        'prune_delete_days',
        'position',
        'bitrate',
        'rate_limit_per_user',
        'color',
        'max_uses',
        'max_age',
        'user_limit',
        'auto_archive_duration',
        'default_auto_archive_duration',
        'communication_disabled_until',
    ]
    new_value: int
    old_value: int


class _AuditLogChange_ListRole(TypedDict):
    key: Literal['$add', '$remove']
    new_value: List[Role]
    old_value: List[Role]


class _AuditLogChange_MFALevel(TypedDict):
    key: Literal['mfa_level']
    new_value: MFALevel
    old_value: MFALevel


class _AuditLogChange_VerificationLevel(TypedDict):
    key: Literal['verification_level']
    new_value: VerificationLevel
    old_value: VerificationLevel


class _AuditLogChange_ExplicitContentFilter(TypedDict):
    key: Literal['explicit_content_filter']
    new_value: ExplicitContentFilterLevel
    old_value: ExplicitContentFilterLevel


class _AuditLogChange_DefaultMessageNotificationLevel(TypedDict):
    key: Literal['default_message_notifications']
    new_value: DefaultMessageNotificationLevel
    old_value: DefaultMessageNotificationLevel


class _AuditLogChange_ChannelType(TypedDict):
    key: Literal['type']
    new_value: ChannelType
    old_value: ChannelType


class _AuditLogChange_IntegrationExpireBehaviour(TypedDict):
    key: Literal['expire_behavior']
    new_value: IntegrationExpireBehavior
    old_value: IntegrationExpireBehavior


class _AuditLogChange_VideoQualityMode(TypedDict):
    key: Literal['video_quality_mode']
    new_value: VideoQualityMode
    old_value: VideoQualityMode


class _AuditLogChange_Overwrites(TypedDict):
    key: Literal['permission_overwrites']
    new_value: List[PermissionOverwrite]
    old_value: List[PermissionOverwrite]


class _AuditLogChange_PrivacyLevel(TypedDict):
    key: Literal['privacy_level']
    new_value: PrivacyLevel
    old_value: PrivacyLevel


class _AuditLogChange_Status(TypedDict):
    key: Literal['status']
    new_value: EventStatus
    old_value: EventStatus


class _AuditLogChange_EntityType(TypedDict):
    key: Literal['entity_type']
    new_value: EntityType
    old_value: EntityType


AuditLogChange = Union[
    _AuditLogChange_Str,
    _AuditLogChange_AssetHash,
    _AuditLogChange_Snowflake,
    _AuditLogChange_Int,
    _AuditLogChange_Bool,
    _AuditLogChange_ListRole,
    _AuditLogChange_MFALevel,
    _AuditLogChange_VerificationLevel,
    _AuditLogChange_ExplicitContentFilter,
    _AuditLogChange_DefaultMessageNotificationLevel,
    _AuditLogChange_ChannelType,
    _AuditLogChange_IntegrationExpireBehaviour,
    _AuditLogChange_VideoQualityMode,
    _AuditLogChange_Overwrites,
    _AuditLogChange_PrivacyLevel,
    _AuditLogChange_Status,
    _AuditLogChange_EntityType,
]


class AuditEntryInfo(TypedDict, total=False):
    delete_member_days: str
    members_removed: str
    channel_id: Snowflake
    message_id: Snowflake
    count: str
    id: Snowflake
    type: Literal['0', '1']
    role_name: str


class _AuditLogEntryOptional(TypedDict, total=False):
    changes: List[AuditLogChange]
    options: AuditEntryInfo
    reason: str


class AuditLogEntry(_AuditLogEntryOptional):
    target_id: Optional[str]
    user_id: Optional[Snowflake]
    id: Snowflake
    action_type: AuditLogEvent


class AuditLog(TypedDict):
    webhooks: List[Webhook]
    users: List[User]
    audit_log_entries: List[AuditLogEntry]
    integrations: List[PartialIntegration]
    threads: List[Thread]
    guild_scheduled_events: List[GuildScheduledEvent]
