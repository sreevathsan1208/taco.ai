import streamlit as st
import json
import os
from google import genai
from google.genai import types

# Initialize Gemini Client
API_KEY = "AQ.Ab8RN6LvtMGJuRrh-3rdMU_tSzEfekdAeRNH8tAidSMCa0pYDg"
client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="Taco AI Companion", page_icon="🌮", layout="centered")

st.title("🌮 Taco: Personal AI Assistant")
st.caption("Live Web Search Grounding & Permanent Command Memory")

# Persistent Memory File Management
MEMORY_FILE = "taco_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"user_name": "Sreevathsan K.", "directives": []}

def save_memory(data):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        st.error(f"Error saving memory: {e}")

memory_data = load_memory()

# Sidebar: View Permanent Directives & Memory
with st.sidebar:
    st.header("🧠 Permanent Memory")
    st.write(f"**User:** {memory_data.get('user_name', 'Boss')}")
    st.subheader("Saved Directives & Rules:")
    directives = memory_data.get("directives", [])
    if directives:
        for idx, item in enumerate(directives, 1):
            st.write(f"{idx}. {item}")
    else:
        st.write("No permanent directives logged yet.")
    
    if st.button("Clear Memory"):
        memory_data["directives"] = []
        save_memory(memory_data)
        st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Past Messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Secret Passcode Trigger Definition
SECRET_PASSCODE = "taco override:"

# Handle User Input
if prompt := st.chat_input("Ask Taco anything or issue a protocol command, Boss..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # 1. Check if the user is issuing a secret passcode command
        if prompt.lower().startswith(SECRET_PASSCODE):
            directive_content = prompt[len(SECRET_PASSCODE):].strip()
            if directive_content:
                memory_data["directives"].append(directive_content)
                save_memory(memory_data)
                reply = f"Passcode accepted, Boss. Permanent directive logged: *\"{directive_content}\"* 🌮"
            else:
                reply = "Passcode accepted, Boss, but no instruction was provided to store."
            
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        else:
            # 2. Normal Query: Search web and apply permanent directives
            with st.spinner("Synthesizing web sources & checking memory..."):
                try:
                    # Compile context string from stored memory
                    directives_str = "\n".join([f"- {d}" for d in memory_data.get("directives", [])])
                    
                    full_prompt = f"""
                    You are Taco, a direct, warm, grounded AI peer for Sreevathsan K. (Boss).
                    
                    Permanent User Directives & Rules to Follow:
                    {directives_str if directives_str else "None yet."}
                    
                    Instructions:
                    1. Answer questions accurately using live web search data.
                    2. Always strictly adhere to any permanent directives logged above by the user.
                    3. Keep your tone natural, helpful, and direct.
                    
                    User Input: "{prompt}"
                    """

                    # Call Gemini API with Google Search grounding tool enabled
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=full_prompt,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(google_search=types.GoogleSearch())],
                            temperature=0.7,
                        ),
                    )
                    
                    reply = response.text
                    st.markdown(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

                except Exception as e:
                    error_message = f"Connection hiccup, Boss. Let's try that again. (Details: {e})"
                    st.markdown(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
