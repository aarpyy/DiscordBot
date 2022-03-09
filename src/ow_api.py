from scrape import *
from os import system

from config import config


def is_battlenet(battlenet: str, platform: str = "PC"):
    url = platform_url(platform)(battlenet)
    return not system(f"exit $(curl -s {url} | "                        # Get info from url
                      f"{str(config['GET'])}/{config['split']} | "      # Split by < for easy searching w/ grep
                      f"egrep -c -i \"profile not found\")")            # Exit with the count of matches. > 1 = DNE


def is_private(battlenet: str, platform: str = "PC"):
    url = platform_url(platform)(battlenet)
    return not system(f"exit $(curl -s {url} | "
                      f"{str(config['GET'])}/{config['split']} | "
                      f"egrep -c -i \"this profile is currently private\")")

if __name__ == "__main__":
    print(is_battlenet("Aarpyy#1975"))
