import apiai
import json
import requests
from sendmsg import *
from dbconn import *
from flask import Flask, request, render_template

app = Flask(__name__)
dbcnn = Dbconn()

# Facebook Messenger Configuration
recipient_id = None
VTK = 'inictelchatbot'
PAT = 'EAAF0ImcKDG4BAKdHLfvAcLwxpF27xWRIHCiZBnkcq2PhadZCDh0dhRRYMz48hfNcQ6GfzbZCfd6jYw4nrZAZAvPtYQbQ0eiN1bGgK7cZBhW' \
      'zxa18cuiE5hnZAqreVmA7j73rhfYj5ZCYqpJgpoZCMa5TD3ASCPri8LUCCklj7zokmHQZDZD'

# Dialogflow Configuration
CAT = 'ed8b909566b94cdbb7901ca7ea8a5e18'

# images
IMG_URL = 'https://i.giphy.com/xT0GqrJNbZkRcr2Jgc.gif'

def nlp_fallback(input_text, session_id):
    dbwrite = False
    ai = apiai.ApiAI(CAT)
    req = ai.text_request()
    req.lang = 'en'  # 'sp' para español
    req.session_id = session_id
    req.query = input_text
    response = req.getresponse()
    raw = json.loads(response.read())
    if raw['status']['code'] == 200:
        # if raw['result']['metadata']['intentName'] == "EnrollStudent":
        #     enrollment = raw['result']['parameters']
        #     if enrollment['TrainingTopics'] is not None and enrollment['TrainingType'] is not None and \
        #             enrollment['TrainingModality'] is not None and enrollment['date'] is not None:
        #         customer_id = session_id
        #         dbres = dbcnn.add_enrollment([customer_id, enrollment])
        #         if not dbres:
        #             raise Exception('MongoDB.Atlas Exception:' + 'Error de escritura en base de datos')
        response_text = raw['result']['fulfillment']['messages'][0]['speech']
    else:
        raise Exception('Dialogflow Exception:' + raw['status']['errorType'])
    return response_text


@app.route('/', methods=['GET'])
def verify():

    # Cuando el endpoint esta registrado como webhook, debe responder el echo de vuelta
    # El valor del 'hub.challenge' se recibe en los argumentos de la consulta
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VTK:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return render_template("index.html"), 200


@app.route('/', methods=['POST'])
def webhook():
    data = request.json
    # log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                # the facebook ID of the person sending you the message
                sender_id = messaging_event["sender"]["id"]
                # the recipient's ID, which should be your page's facebook ID
                recipient_id = messaging_event["recipient"]["id"]
                if messaging_event.get("message"):  # someone sent us a message
                    if "text" in messaging_event["message"]:
                        message_text = messaging_event["message"]["text"]
                        # if message_text == "quick":
                        #     send_quick_reply(sender_id, PAT)
                        response = nlp_fallback(message_text, sender_id)
                        send_message(sender_id, str(response), PAT)
                    if "attachments" in messaging_event["message"]:  # contains an image, location or other
                        attachment = messaging_event["message"]["attachments"][0]
                        # if attachment['type'] == 'image':
                        #     message_image = attachment["payload"]["url"]
                        #     send_location_message(sender_id, "Please let me know where can we pick the bike up", PAT)
    return "ok", 200

# def send_message(recipient_id, message_text):
#     params = {
#         "access_token": PAT
#     }
#     headers = {
#         "Content-Type": "application/json"
#     }
#     data = json.dumps({
#         "recipient": {
#             "id": recipient_id
#         },
#         "message": {
#             "text": message_text
#         }
#     })
#     r = requests.post("https://graph.facebook.com/v4.0/me/messages", params=params, headers=headers, data=data)
#     if r.status_code != 200:
#         print(r.status_code)
#         print(r.text)


if __name__ == '__main__':
    parameters = {
        "TrainingTopics": "Basics of Drone Technology",
        "TrainingType": "Single course",
        "TrainingModality": "online",
        "date": "2020-06-01"
    }
    # dbres = dbcnn.add_enrollment([2, parameters])
    app.run(debug=True, port=5500)
