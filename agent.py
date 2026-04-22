import streamlit as st
import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# load knowledge base from json file
with open("knowledge_base.json", "r") as f:
    knowledge_base = json.load(f)

# convert knowledge base to readable text
# so we can pass it to the LLM
kb_text = json.dumps(knowledge_base, indent=2)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def mock_lead_capture(name, email, platform):
    # this simulates saving lead to a database
    print(f"Lead captured: {name}, {email}, {platform}")
    return f"Lead captured successfully for {name}!"


def detect_intent(message, conversation_history):
    # ask LLM to classify what user wants
    intent_prompt = f"""
    Classify this user message into one of these intents:
    1. greeting - just saying hi or hello
    2. product_inquiry - asking about features or pricing
    3. high_intent - ready to sign up or buy

    User message: {message}

    Reply with ONLY one word: greeting, product_inquiry, or high_intent
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are an intent classifier. Reply with one word only."},
            {"role": "user", "content": intent_prompt}
        ],
        temperature=0.1
        # very low temperature for consistent classification
    )

    intent = response.choices[0].message.content.strip().lower()

    # make sure we only get valid intents
    if intent not in ["greeting", "product_inquiry", "high_intent"]:
        intent = "product_inquiry"

    return intent


def get_agent_response(conversation_history, user_message, lead_info):
    # build system prompt with knowledge base
    system_prompt = f"""
    You are a helpful sales agent for AutoStream, 
    a SaaS product for automated video editing.

    Here is your knowledge base:
    {kb_text}

    Your job:
    1. Answer questions about AutoStream accurately
       using ONLY the knowledge base above
    2. Be friendly and helpful
    3. When user shows interest in buying,
       collect their name, email and platform
    4. Keep responses short and conversational

    Current lead information collected:
    Name: {lead_info.get('name', 'Not collected')}
    Email: {lead_info.get('email', 'Not collected')}
    Platform: {lead_info.get('platform', 'Not collected')}

    If user wants to sign up:
    - First ask for name if not collected
    - Then ask for email if not collected
    - Then ask for platform if not collected
    - Once all three collected, confirm the lead capture

    Do not ask for information already collected.
    """

    messages = [{"role": "system", "content": system_prompt}]

    # add conversation history so agent remembers context
    for msg in conversation_history:
        messages.append(msg)

    # add current user message
    messages.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content


def extract_lead_info(message, field):
    # extract specific info from user message
    extract_prompt = f"""
    Extract the {field} from this message.
    Message: {message}

    Rules:
    - If extracting email, return only the email address
    - If extracting name, return only the person's name
    - If extracting platform, return only the platform name
    - If not found, return "NOT_FOUND"

    Reply with the extracted value only.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You extract specific information from messages."},
            {"role": "user", "content": extract_prompt}
        ],
        temperature=0.1
    )

    result = response.choices[0].message.content.strip()
    return None if result == "NOT_FOUND" else result


def process_message(user_message, conversation_history, lead_info):
    
    # step 1: detect intent
    intent = detect_intent(user_message, conversation_history)
    
    # step 2: try to extract info from EVERY message
    # not just when intent is high_intent
    # because user might give email in any message
    
    if not lead_info.get('name'):
        # we dont have name yet, try to extract it
        name = extract_lead_info(user_message, "name")
        if name and name != "NOT_FOUND":
            lead_info['name'] = name

    elif not lead_info.get('email'):
        # we have name but no email, try to extract email
        email = extract_lead_info(user_message, "email")
        if email and email != "NOT_FOUND":
            lead_info['email'] = email

    elif not lead_info.get('platform'):
        # we have name and email, try to extract platform
        platform = extract_lead_info(user_message, "platform")
        if platform and platform != "NOT_FOUND":
            lead_info['platform'] = platform

    # step 3: check if all info collected
    lead_captured = False
    capture_message = ""

    if (lead_info.get('name') and
            lead_info.get('email') and
            lead_info.get('platform') and
            not st.session_state.get('lead_captured', False)):

        result = mock_lead_capture(
            lead_info['name'],
            lead_info['email'],
            lead_info['platform']
        )
        lead_captured = True
        capture_message = result

    # step 4: get agent response
    response = get_agent_response(
        conversation_history,
        user_message,
        lead_info
    )

    return response, lead_info, lead_captured, capture_message, intent
    # step 3: check if we have all lead info
    lead_captured = False
    capture_message = ""

    if (lead_info.get('name') and
            lead_info.get('email') and
            lead_info.get('platform')):

        # all info collected - trigger lead capture!
        result = mock_lead_capture(
            lead_info['name'],
            lead_info['email'],
            lead_info['platform']
        )
        lead_captured = True
        capture_message = result

    # step 4: get agent response
    response = get_agent_response(
        conversation_history,
        user_message,
        lead_info
    )

    return response, lead_info, lead_captured, capture_message, intent