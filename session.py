from replit import db
from discord import Guild, Member, Role
from discord.ext.commands import Bot
from typing import MutableMapping, MutableSequence


def dict_copy(d: MutableMapping):
    cpy = {}
    for key, value in d.items():
        if isinstance(value, MutableSequence):
            cpy[key] = value[:]
        elif isinstance(value, MutableMapping):
            cpy[key] = dict_copy(value)
        else:
            cpy[key] = value
    return cpy


class Session:

    def __init__(self, bot: Bot):
        self._db = dict_copy(db)
        self._bot = bot

        guild: Guild
        role: Role

        self._roles = {}

        for guild in bot.guilds:
            for role in guild.roles:
                self._roles[role.id] = role.members

    async def clear(self):
        from replit import db
        for key, value in self._db.items():
            db[key] = value

        guild: Guild
        role: Role
        member: Member

        for guild in self._bot.guilds:
            for role in guild.roles:
                if role.id not in self._roles:
                    await role.delete()
                else:
                    for member in role.members:
                        if member not in self._roles[role.id]:
                            await member.remove_roles(role)
