import streamlit as st
from agent import process_message

st.set_page_config(
    page_title="AutoStream Assistant",
    page_icon="🎬",
    layout="centered"
)

st.title("AutoStream AI Assistant")
st.write("Ask me anything about AutoStream!")
st.divider()

# initialize session state
# session state persists data across reruns
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
    # stores full chat history for LLM memory

if "messages" not in st.session_state:
    st.session_state.messages = []
    # stores messages for UI display

if "lead_info" not in st.session_state:
    st.session_state.lead_info = {}
    # stores collected lead details

if "lead_captured" not in st.session_state:
    st.session_state.lead_captured = False
    # tracks if lead was already captured

# show welcome message on first load
if len(st.session_state.messages) == 0:
    welcome = "Hi! I am AutoStream's virtual assistant. I can help you with pricing, features, and getting started. What would you like to know?"
    st.session_state.messages.append({
        "role": "assistant",
        "content": welcome
    })

# display all previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# show lead capture success banner
if st.session_state.lead_captured:
    st.success("Lead captured successfully! Our team will contact you soon.")

# show what info has been collected so far
# better sidebar with cleaner display
with st.sidebar:
    st.subheader("Lead Information")
    st.divider()
    
    # show each field with checkmark
    name = st.session_state.lead_info.get('name')
    email = st.session_state.lead_info.get('email')
    platform = st.session_state.lead_info.get('platform')
    
    if name:
        st.success(f"Name: {name}")
    else:
        st.warning("Name: Not collected")
    
    if email:
        st.success(f"Email: {email}")
    else:
        st.warning("Email: Not collected")
    
    if platform:
        st.success(f"Platform: {platform}")
    else:
        st.warning("Platform: Not collected")
    
    st.divider()
    
    # show lead status
    if st.session_state.lead_captured:
        st.success("Lead Captured!")
    else:
        st.info("Lead: In Progress")

# chat input box at bottom
user_input = st.chat_input("Type your message here...")

if user_input:
    # show user message immediately
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.write(user_input)

    # get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):

            response, updated_lead, captured, capture_msg, intent = process_message(
                user_input,
                st.session_state.conversation_history,
                st.session_state.lead_info
            )

            st.write(response)

            # show intent badge
            intent_colors = {
                "greeting": "blue",
                "product_inquiry": "orange",
                "high_intent": "green"
            }
            st.caption(f"Intent detected: {intent}")

    # update session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # update conversation history for LLM memory
    st.session_state.conversation_history.append({
        "role": "user",
        "content": user_input
    })
    st.session_state.conversation_history.append({
        "role": "assistant",
        "content": response
    })

    # update lead info
    st.session_state.lead_info = updated_lead

    # mark lead as captured
    if captured:
        st.session_state.lead_captured = True

    st.rerun()
    # rerun refreshes the page to show new messages