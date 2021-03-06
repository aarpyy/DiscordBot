from typing import Optional
from discord import Colour, Role, Guild

categ_short: dict[str, str]
categ_major: tuple[str, ...]
mention_tag: str
no_tag: str
tags: tuple[str, ...]
obw_color: Colour

def format_time(stat: str) -> str: ...
def format_stat(ctg: str, stat: str) -> str: ...
def format_role(role: Role) -> str: ...
async def get_role_obj(guild: Guild, role: str) -> Optional[Role]: ...
async def force_role_obj(guild: Guild, role: str, **kwargs: str) -> Role: ...
async def delete_role(role: Role, name: str = ...) -> None: ...
def remove_role(role: str) -> None: ...
def rename_role(before: str, after: str) -> None: ...
def generate_roles(bnet: str) -> set[str]: ...
async def update_user_roles(guild: Guild, disc: str, bnet: str) -> None: ...
def adjust_roles(db_roles: set[str], new_roles: set[str], disc_roles: set[str]) -> tuple[set[str], set[str]]: ...
