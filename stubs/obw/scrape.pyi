from .config import cURL as cURL, path_split as path_split
from .obw_errors import PrivateProfileError as PrivateProfileError, ProfileNotFoundError as ProfileNotFoundError
from typing import Callable, Dict, Tuple

def platform_url(platform: str) -> Callable[[str], str]: ...
def scrape_play_ow(bnet: str, pf: str = ...) -> Tuple[Dict, Dict]: ...
