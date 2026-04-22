# AutoStream AI Sales Agent

A conversational AI agent built for AutoStream,
a fictional SaaS company providing automated 
video editing tools for content creators.

Built as part of the ServiceHive - Inflx 
Machine Learning Intern Assignment.

## Demo Video
https://youtu.be/Mt1NsKG5IME

## Project Structure
autostream-agent/
├── app.py                 
├── agent.py               
├── knowledge_base.json    
├── requirements.txt       
├── .env.example           
└── README.md              

## How to Run Locally

1. Clone this repository
2. Install dependencies:
   pip install -r requirements.txt
   
3. Create .env file:
   cp .env.example .env
   Add your GROQ_API_KEY in .env file
   Get free key at: console.groq.com

4. Run the app:
   streamlit run app.py

5. Open browser at:
   http://localhost:8501

## Architecture Explanation

The project consists of two main components:

**Agent (agent.py)**
The agent uses Groq API with Llama 3.3 70b model.
Each user message goes through three stages.
First intent detection classifies the message
as greeting, product inquiry or high intent.
Then the knowledge base loaded from a local
JSON file is passed as context to the LLM
which acts as a simple RAG pipeline ensuring
accurate answers about pricing and policies.
Finally conversation history is maintained
as a list and passed with every API call
so the agent remembers context across turns.

**UI (app.py)**
Built with Streamlit using session state
to persist conversation history lead info
and captured status across interactions.
The sidebar shows real time updates as
lead information is collected.

**Why Groq with Llama 3.3**
The assignment specified Gemini or GPT.
I attempted Gemini but faced quota restrictions
on the free tier. Groq provides free reliable
access to Llama 3.3 70b which is a capable
open source model that handles intent detection
RAG based responses and lead extraction well.

**Knowledge Base (RAG)**
Pricing features and company policies are
stored in knowledge_base.json. This file is
loaded at startup and injected into the system
prompt giving the agent accurate information
to answer user questions without hallucinating.

**State Management**
Conversation history is stored as a list of
message dictionaries. Each new API call receives
the full history maintaining context across
5 to 6 conversation turns as required.

## WhatsApp Integration via Webhooks

To deploy this agent on WhatsApp:

1. Create a Meta Developer account at
   developers.facebook.com

2. Create a WhatsApp Business API app
   and get a phone number

3. Build a webhook server using FastAPI:
   - POST endpoint receives incoming messages
   - Extract message text from webhook payload
   - Pass to process_message() function
   - Send response back via WhatsApp API

4. Example webhook handler:
   from fastapi import FastAPI, Request
   import requests
   
   app = FastAPI()
   
   @app.post("/webhook")
   async def webhook(request: Request):
       data = await request.json()
       message = data["entry"][0]["changes"][0]
                     ["value"]["messages"][0]["text"]["body"]
       phone = data["entry"][0]["changes"][0]
                    ["value"]["messages"][0]["from"]
       
       response, lead_info, captured, msg, intent = process_message(
           message, conversation_history, lead_info
       )
       
       send_whatsapp_message(phone, response)
       return {"status": "ok"}

5. Deploy webhook server on Render or Railway
   for a public URL

6. Register the webhook URL in Meta Developer
   Console under WhatsApp configuration

## Agent Capabilities

- Intent Detection: greeting, product inquiry, high intent
- RAG Pipeline: answers from local knowledge base
- Lead Collection: name, email, creator platform
- Tool Execution: mock_lead_capture() triggered
  only after all three details collected
- Memory: retains context across conversation turns
