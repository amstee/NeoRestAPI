import redis
from loader import neo_config

neo_config.load_config()

db = redis.from_url(neo_config.redis_url)
db1 = redis.from_url(neo_config.redis_url, db=1)


def clean_redis_databases():
    for key in db.scan_iter():
        print("Deletion of key from db --> ", key)
        db.delete(key)
    print("DB Cleaned\n")
    for key in db1.scan_iter():
        print("Deletion of key from db1 --> ", key)
        db1.delete(key)
    print("DB1 Cleaned")


if __name__ == "__main__":
    clean_redis_databases()
