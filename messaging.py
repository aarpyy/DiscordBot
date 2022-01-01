from replit import db

from discord import Message, TextChannel, User, Member, DMChannel, GroupChannel, Reaction, Emoji, Guild, abc
from discord.ext.commands import Bot

from config import Key
from battlenet import get_top
from request import getuser, get_role_obj, force_role_obj
from obwrole import give_role, donate_role, mention_tag, obw_color
import database

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


def valid_channel(channel: abc.Messageable) -> bool:
    return isinstance(channel, TextChannel) and channel.name in superlatives


def valid_reaction(reaction: Reaction):
    return reaction.custom_emoji and reaction.emoji.name in reaction_scores


def add_index(disc: str, message: Message):
    db[Key.MMBR][disc][Key.RXN][message.id] = {Key.TIME: message.created_at.timestamp(), Key.SCORE: {}}


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


def del_reaction(disc: str) -> None:
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


async def log_reaction(author: Member, reaction: Reaction):
    message = reaction.message  # type: Message
    channel = message.channel  # type: TextChannel
    disc = str(author)
    emoji_name = reaction.emoji.name
    superlative = superlatives[channel.name]

    print(f"Message.id: {message.id}")

    m_id = message.id

    if m_id not in db[Key.MMBR][disc][Key.RXN]:
        print("Adding index")
        if len(db[Key.MMBR][disc][Key.RXN]) >= nmessages:
            del_reaction(disc)
        add_index(disc, message)

    database.dump()

    # Find the change in reaction count whether negative or postiive
    nadded = reaction.count - db[Key.MMBR][disc][Key.RXN][m_id][Key.SCORE].get(emoji_name, 0)

    # Set this reaction count to new count recorded
    db[Key.MMBR][disc][Key.RXN][m_id][Key.SCORE][emoji_name] = reaction.count

    # Adjust overall score accordingly
    db[Key.MMBR][disc][Key.SCORE].setdefault(superlative, 0)
    db[Key.MMBR][disc][Key.SCORE][superlative] += nadded * reaction_scores[emoji_name]

    top_user = get_top(superlative)
    if db[Key.MMBR][top_user][Key.SCORE][superlative] < db[Key.MMBR][disc][Key.SCORE][superlative]:
        kwargs = dict(
            name=superlative,
            color=obw_color,
            mentionable=True
        )
        superlative_role = await force_role_obj(author.guild, mention_tag + superlative, **kwargs)
        donated = False
        for member in superlative_role.members:  # type: Member
            if str(member) == top_user:
                await donate_role(author.guild, member, author, superlative_role)
                donated = True
                break

        if not donated:
            await give_role(author.guild, author, superlative_role)
