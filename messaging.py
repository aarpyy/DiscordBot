from replit import db

from discord import Message, TextChannel, User, Member, DMChannel, GroupChannel, Reaction, Emoji, Guild
from discord.ext.commands import Bot

from config import Key
from battlenet import get_top
from request import getuser

from typing import Union, List, Dict


# Constants relating to superlatives given to users as follows:
# If a message is sent in one of the provided reaction channels in any guild and that message
# is reacted to with a custom emoji with a name listed in reaction_scores then it is scored based
# on the provided scores. The channel is then used to determine the superlative granted to the top
# scoring member in that channel. nmessages determines the n most recent reacted-to-messages
# that the user is scored on, so that the superlative is updated to reflect current standings.
reaction_scores = {"Bronze": -2, "Silver": -1, "Gold": 0, "Platinum": 1, "Diamond": 2, "Master": 3, "Grandmaster": 4}
superlatives = {"shitpost": "Top Shitposter", "test": "Top Tester lol"}
nmessages = 50


def valid_channel(channel: TextChannel) -> bool:
    return isinstance(channel, GroupChannel) and channel.name in superlatives


def valid_reaction(reaction: Reaction):
    return reaction.custom_emoji and reaction.emoji.name in reaction_scores


def add_index(disc: str, message: Message, score: int):
    db[Key.MMBR][disc][Key.RXN][message.id] = {Key.TIME: message.created_at.timestamp(), Key.SCORE: score}


def gen_reactions(reactions: List[Reaction]):
    """
    Returns a generator that iterates over all custom emojis listed in reaction_scores.

    :param reactions: list of reactions to message
    :return: generator of relevant reactions
    """

    for reaction in reactions:
        if valid_reaction(reaction):
            yield reaction


def message_score(message: Message) -> List[int]:
    score = []
    for reaction in gen_reactions(message.reactions):
        score.append(reaction_scores[reaction.emoji.name])
    return score


def rm_reaction(disc: str) -> None:
    """
    Removes the oldest message user received a reaction to.

    :param disc: username
    :return: None
    """

    oldest_id = min(db[Key.MMBR][disc][Key.RXN], key=lambda x: db[Key.MMBR][disc][Key.RXN][x][Key.TIME])
    del db[Key.MMBR][disc][Key.RXN][oldest_id]


def pop_reaction(disc: str) -> Dict[str, int]:
    """
    Pops the oldest message user received a reaction to.

    :param disc: username
    :return: reaction index
    """

    oldest_id = min(db[Key.MMBR][disc][Key.RXN], key=lambda x: db[Key.MMBR][disc][Key.RXN][x][Key.TIME])
    index = db[Key.MMBR][disc][Key.RXN][oldest_id]
    del db[Key.MMBR][disc][Key.RXN][oldest_id]
    return index


def add_reaction(bot: Bot, guild: Guild, author: Member, message: Message, reaction: Reaction):
    disc = str(author)
    score = reaction_scores[reaction.emoji.name] * reaction.count
    if message.id in db[Key.MMBR][disc][Key.RXN]:
        db[Key.MMBR][disc][Key.RXN][Key.SCORE] += score
    else:
        add_index(disc, message, score)
        if len(db[Key.MMBR][disc][Key.RXN]) >= nmessages:
            rm_reaction(disc)

    db[Key.MMBR][disc][Key.SCORE] += score
    top_user = get_top()
    if db[Key.MMBR][top_user][Key.SCORE] < db[Key.MMBR][disc][Key.SCORE]:
        former = await getuser(bot, disc)


