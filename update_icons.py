from replit import db

if __name__ == '__main__':
  db['ranks'] = dict(grandmaster="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-GrandmasterTier.png", master="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-MasterTier.png", diamond="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-DiamondTier.png", platinum="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-PlatinumTier.png", gold="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-GoldTier.png", silver="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-SilverTier.png", bronze="https://d1u1mce87gyfbn.cloudfront.net/game/rank-icons/rank-BronzeTier.png")

  db['roles'] = dict(tank="https://static.playoverwatch.com/img/pages/career/icon-tank-8a52daaf01.png", support="https://static.playoverwatch.com/img/pages/career/icon-support-46311a4210.png", offense="https://static.playoverwatch.com/img/pages/career/icon-offense-6267addd52.png")
