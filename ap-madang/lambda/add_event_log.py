import json
import logging
import pymongo
import mongo_config

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred

# client = pymongo.MongoClient("mongodb://{}:{}@meetup-event.buzao.mongodb.net/events?retryWrites=true&w=majority".format(
#         mongo_config.mongo_username, mongo_config.mongo_password
#     ))
# db = client.test

# client = pymongo.MongoClient(
#     "mongodb://{}:{}@meetup-events.cluster-c8zwh9jcttzy.ap-northeast-2.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false".format(
#         mongo_config.mongo_username, mongo_config.mongo_password
#     )
# )
# client = MongoClient("meetup-events.cluster-c8zwh9jcttzy.ap-northeast-2.docdb.amazonaws.com", 27017, username=mongo_config.mongo_username, password=mongo_config.mongo_password, ssl=True, ssl_cert_reqs=ssl.CERT_NONE)

# Set database
# db = client.dev


def lambda_handler(event, context):
    logger.info("?!?!?!?")
    print("!!")
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://{}:{}@meetup-event.buzao.mongodb.net/events?retryWrites=true&w=majority".format(
                mongo_config.mongo_username, mongo_config.mongo_password
            )
        )
        db = client.events
        collection = db.dev
    except:
        logger.error("Failed to connect to MongoDB")
        print("!!")
    print(client.list_database_names())

    # events = db.events

    collection.insert_one({"hello": "Amazon DocumentDB"})

    # TODO implement
    return {
        "statusCode": 200,
        "body": json.dumps("Hello from Lambda!"),
        "db": str(client.list_database_names()),
    }


lambda_handler(None, None)
