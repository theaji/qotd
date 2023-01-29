import json
import boto3
import os
import urllib3

topic = os.environ['TOPIC']
region = os.environ['REGION']

client = boto3.client('sns', region_name=region)

site = urllib3.PoolManager()
url = site.request("GET", "https://quotes.rest/qod?language=en", timeout=10)
resp = url.data
newResp = json.loads(resp)


def lambda_handler(event, context):
    
    if url.status == 200:
        quote = newResp["contents"]["quotes"][0]["quote"]
        author = newResp["contents"]["quotes"][0]["author"]
        heading = "Good Morning! \n"
        headingb = "Your Quote of the Day is: \n"
        messagea = heading + "\n" + headingb + "\n" + quote + "\n" + "- " + author
        subj = "Your Daily Quote!"
        response = client.publish(
          TopicArn=topic,
          Subject=subj,
          Message=messagea
          )
        print(messagea)
        return {
            "statusCode": 200,
            "body": "Message sent successfully"
        }
    else:
        print("There was an issue retrieving quote!!")
