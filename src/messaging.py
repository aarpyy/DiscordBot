from .config import db
from discord import Message, TextChannel, Member, Reaction, abc
from .roles import mention_tag, obw_color, force_role_obj
from .db_keys import *
from . import database

from typing import List, Dict

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
    db[MMBR][disc][RXN][str(message.id)] = {TIME: message.created_at.timestamp(), SCORE: {}}


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

    oldest_id = min(db[MMBR][disc][RXN], key=lambda x: db[MMBR][disc][RXN][x][TIME])
    del db[MMBR][disc][RXN][oldest_id]


def pop_reaction(disc: str) -> Dict[str, int]:
    """
    Pops the oldest message user received a reaction to.

    :param disc: username
    :return: reaction index
    """

    oldest_id = min(db[MMBR][disc][RXN], key=lambda x: db[MMBR][disc][RXN][x][TIME])
    index = db[MMBR][disc][RXN][oldest_id]
    del db[MMBR][disc][RXN][oldest_id]
    return index


async def log_reaction(author: Member, reaction: Reaction):
    message = reaction.message  # type: Message
    channel = message.channel  # type: TextChannel
    disc = str(author)
    emoji_name = reaction.emoji.name
    superlative = superlatives[channel.name]

    print(f"Message.id: {message.id}")

    m_id = str(message.id)

    if m_id not in db[MMBR][disc][RXN]:
        print("Adding index")
        if len(db[MMBR][disc][RXN]) >= nmessages:
            del_reaction(disc)
        add_index(disc, message)

        for rxn in message.reactions:   # type: Reaction
            if valid_reaction(rxn):
                if str(rxn) in db[MMBR][disc][RXN][str(message.id)][SCORE]:
                    db[MMBR][disc][RXN][str(message.id)][SCORE][str(rxn)] += reaction_scores[str(rxn)]
                else:
                    db[MMBR][disc][RXN][str(message.id)][SCORE][str(rxn)] = reaction_scores[str(rxn)]
    else:
        # db[MMBR][disc][SCORE] += diff
        pass
        # If message already there, find the difference in score between new score and old, update in database,
        # adjust global user score in that channel

    database.dump()

    # Find the change in reaction count whether negative or postiive
    nadded = reaction.count - db[MMBR][disc][RXN][m_id][SCORE].get(emoji_name, 0)

    # Set this reaction count to new count recorded
    db[MMBR][disc][RXN][m_id][SCORE][emoji_name] = reaction.count

    # Adjust overall score accordingly
    db[MMBR][disc][SCORE].setdefault(superlative, 0)
    db[MMBR][disc][SCORE][superlative] += nadded * reaction_scores[emoji_name]

    # Member: {"shitpost": 5

    top_user = None
    if db[MMBR][top_user][SCORE][superlative] < db[MMBR][disc][SCORE][superlative]:
        kwargs = dict(
            name=superlative,
            color=obw_color,
            mentionable=True
        )
        superlative_role = await force_role_obj(author.guild, mention_tag + superlative, **kwargs)
        donated = False
        for member in superlative_role.members:  # type: Member
            if str(member) == top_user:
                # await donate_role(author.guild, member, author, superlative_role)
                donated = True
                break

        if not donated:
            # await give_role(author.guild, author, superlative_role)
            pass
