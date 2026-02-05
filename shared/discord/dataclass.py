from dataclasses import dataclass

__all__ = [
    "INTERACTION_CALLBACK_TYPE",
    "TYPE",
    "COMPONENT_TYPE",
    "TEXT_INPUT_STYLE",
    "BUTTON_STYLE",
    "CHANNEL_TYPE",
]


@dataclass
class INTERACTION_CALLBACK_TYPE:
    # https://discord.com/developers/docs/interactions/receiving-and-responding#interaction-response-object
    PONG = 1
    ACK_NO_SOURCE = 2
    CHANNEL_MESSAGE_WITH_SOURCE = 4
    DEFERRED_CHANNEL_MESSAGE_WITH_SOURCE = 5
    DEFERRED_UPDATE_MESSAGE = 6
    UPDATE_MESSAGE = 7
    APPLICATION_COMMAND_AUTOCOMPLETE_RESULT = 8
    MODAL = 9
    PREMIUM_REQUIRED = 10


@dataclass
class TYPE:
    PING = 1
    BUTTON = 3
    MODAL = 5


@dataclass
class COMPONENT_TYPE:
    # https://discord.com/developers/docs/interactions/message-components#component-object-component-types
    ACTION_ROW = 1
    BUTTON = 2
    STRING_SELECT = 3
    TEXT_INPUT = 4
    USER_SELECT = 5
    ROLE_SELECT = 6
    MENTIONABLE_SELECT = 7
    CHANNEL_SELECT = 8


@dataclass
class TEXT_INPUT_STYLE:
    # https://discord.com/developers/docs/interactions/message-components#text-input-object-text-input-interaction
    SHORT = 1
    PARAGRAPH = 2


@dataclass
class BUTTON_STYLE:
    # https://discord.com/developers/docs/interactions/message-components#button-object-button-styles
    PRIMARY = 1
    SECONDARY = 2
    SUCCESS = 3
    DANGER = 4
    LINK = 5


@dataclass
class CHANNEL_TYPE:
    # https://discord.com/developers/docs/resources/channel#channel-object-channel-types
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13
    GUILD_DIRECTORY = 14
    GUILD_FORUM = 15
    GUILD_MEDIA = 16
