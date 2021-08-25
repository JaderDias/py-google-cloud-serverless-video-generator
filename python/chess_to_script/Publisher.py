from google.cloud import pubsub
import json
import Constants

def publish(topic, data):
    publisher = pubsub.PublisherClient()
    topic_name = 'projects/{project_id}/topics/{topic}'.format(
            project_id=Constants.PROJECT_NAME,
            topic=topic,
    )
    print("topic: {0}".format(topic_name))
    encoded_data = json.dumps(data).encode("utf-8")
    publisher.publish(topic_name, encoded_data)