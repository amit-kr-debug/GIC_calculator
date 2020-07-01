from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import calculator

app = Flask(__name__)


@app.route("/")
def hello():
    return "Webserver"


@app.route("/calculator", methods=['POST'])
def user_sms_reply():
    msg = request.form.get('Body')
    reply = MessagingResponse()

    if msg == 'hi' or msg == 'Hi' or msg == 'hii' or msg == 'Hey' or msg == 'hello' or msg == 'hey':
        resp = reply.message(
            "Enter Start and End Dates: ")
        # resp1.message("testing")
    else:
        Total, str3, str4 = calculator.calculator(msg[0:11], msg[11:])
        resp = reply.message("Deposits till 1998\n"+str3)
        resp1 = reply.message("Deposits after 1998\n"+str4+"\n Total Sum = "+str(Total))
    return str(reply)


# 12 06 1998 03 07 2000
if __name__ == "__main__":
    app.run(debug=True)
