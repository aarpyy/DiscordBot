

if __name__ == "__main__":
    from os import getenv
    if not getenv("REPLIT_DB_URL"):
        from dotenv import load_dotenv
        load_dotenv(".env")

    from replit import db
    print(type(db))
    for k, v in db.items():
        print(f"{k}: {v}")