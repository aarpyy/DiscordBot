from typing import Optional

guilds: str
members: str
battlenets: str
primary: Optional[str]
_id: int
reactions: None   # Not actually None, just not known
score: None       # Not actually None, just not known
active: bool
private: bool
hidden: bool
platform: str
ranks: str
stats: str
roles: str

db = {
  "guilds": {
    "guild1": {
      "members": {
        "member1": {
          "id": "0001",
          "battlenets": ["battlenet1", "battlenet2"],
          "primary": "battlenet1",
          "reactions": {},    # TODO: Finish reactions
          "score": {}         # TODO: Finish score
        },
        "member2": {
          "id": "0002",
          "battlenets": [],
          "primary": None,
          "reactions": {},
          "score": {}
        }
      }
    }
  },
  "battlenets": {
    "battlenet1": {
      "active": True,
    }
  }
}
