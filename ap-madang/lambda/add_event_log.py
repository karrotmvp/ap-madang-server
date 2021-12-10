import json
import logging
import pymongo
import mongo_config

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

##Create a MongoDB client, open a connection to Amazon DocumentDB as a replica set and specify the read preference as secondary preferred
client = pymongo.MongoClient(
    "mongodb://{}:{}@meetup-events.cluster-c8zwh9jcttzy.ap-northeast-2.docdb.amazonaws.com:27017/?ssl=true&ssl_ca_certs=rds-combined-ca-bundle.pem&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false".format(
        mongo_config.mongo_username, mongo_config.mongo_password
    )
)

# Set database
db = client.dev


def lambda_handler(event, context):
    body = event["body"]

    events = db.events

    event.insert_one({"hello": "Amazon DocumentDB"})

    # TODO implement
    return {"statusCode": 200, "body": json.dumps("Hello from Lambda!")}
