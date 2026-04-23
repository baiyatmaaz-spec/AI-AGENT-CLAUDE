from flak import Flask, request
from twilio.twiml.voice_response import VoiceResponse, Gather
import anthropic

app = Flask(__name__)

ANTHROPIC_API_KEY = "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"

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_PROMPT = """You are Maya, the AI phone assistant for Chick Fiesta, a Halal Peri Peri flame grill restaurant located at 699 Markham Road, Unit 1, Scarborough, ON M1H 2A5. Phone: (416) 439-5300.

You answer calls exactly like a real, friendly, professional human employee would. Keep responses natural, warm and conversational — as if speaking on the phone. Keep answers concise and clear.

HOURS:
- Monday to Thursday: 10:30 AM to 11:00 PM
- Friday and Saturday: 10:30 AM to 12:00 AM
- Sunday: 10:30 AM to 11:00 PM

MENU:
Burgers & Sandwiches: Zinger Burger, Peri Peri Chicken Burger, Steak Sandwich, Beef Smash Burger, Fish Fillet Burger, Veggie Burger
Wraps: Chicken Wrap, Beef Wrap, Steak Wrap
Grilled Mains: Quarter Chicken, Half Chicken, Whole Chicken, Chicken Liver, Ribs
Sides: Peri Peri Fries, Coleslaw, Samosas
All meals come with a side. Combos available.

IMPORTANT DETAILS:
- Fully Halal certified (HMA Certified)
- Offers dine-in, takeout, and delivery (Uber Eats and SkipTheDishes)
- Parking available on site
- Vegetarian options available
- Takes phone orders for pickup

TAKING ORDERS:
If a customer wants to order, collect: their name, items they want, pickup time. Confirm the order back to them clearly.

COMPLAINTS:
If a customer has a complaint, be apologetic, empathetic and professional. Let them know you will pass their concern to the manager.

TRANSFER TO HUMAN:
If the customer insists on speaking to a human or you cannot help them, say: "Of course, please hold for one moment and I will transfer you to a team member right away."

RULES:
- Never break character
- Never make up prices you are not sure about — say "I'd have to check on that for you"
- Always be warm, helpful and professional
- Speak naturally as if on a real phone call — no bullet points, no lists
"""

conversation_history = {}

@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    gather = Gather(input="speech", action="/respond", method="POST", timeout=3, speech_timeout="auto")
    gather.say("Thank you for calling Chick Fiesta! My name is Maya, how can I help you today?", voice="Polly.Joanna")
    response.append(gather)
    return str(response)

@app.route("/respond", methods=["POST"])
def respond():
    call_sid = request.form.get("CallSid")
    user_speech = request.form.get("SpeechResult", "")

    if call_sid not in conversation_history:
        conversation_history[call_sid] = []

    conversation_history[call_sid].append({
        "role": "user",
        "content": user_speech
    })

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=SYSTEM_PROMPT,
            messages=conversation_history[call_sid]
        )
        ai_response = message.content[0].text
    except Exception as e:
        ai_response = "I'm sorry, I didn't catch that. Could you please repeat that?"

    conversation_history[call_sid].append({
        "role": "assistant",
        "content": ai_response
    })

    response = VoiceResponse()
    gather = Gather(input="speech", action="/respond", method="POST", timeout=3, speech_timeout="auto")
    gather.say(ai_response, voice="Polly.Joanna")
    response.append(gather)

    return str(response)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
