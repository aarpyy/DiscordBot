def is_active(bnet: str) -> bool: ...
def is_hidden(bnet: str) -> bool: ...
def is_primary(disc: str, bnet: str) -> bool: ...
def is_private(bnet: str) -> bool: ...
def get_top(superlative: str) -> bool: ...
def hide(bnet: str) -> bool: ...
def deactivate(bnet: str) -> bool: ...
def create_index(bnet: str, pf: str) -> bool: ...
def add(disc: str, bnet: str, pf: str) -> bool: ...
def update(bnet: str) -> None: ...
def remove(bnet: str, gld: str = ..., disc: str = ...) -> None: ...
