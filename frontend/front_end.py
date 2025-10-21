import streamlit as st
import requests
import time

API_URL = "http://localhost:8000"

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "token" not in st.session_state:
    st.session_state["token"] = None

if "show_register" not in st.session_state:
    st.session_state["show_register"] = False

if "show_login" not in st.session_state:
    st.session_state["show_login"] = False

if "messages" not in st.session_state:
    st.session_state["messages"] = []

def load_chat_history(collection_id):
    """Load chat history for a specific collection"""
    try:
        headers = get_headers()
        response = requests.get(f"{API_URL}/chat-history/{collection_id}", headers=headers)
        if response.status_code == 200:
            chat_history = response.json()
            messages = []
            for chat in chat_history:
                messages.append({"role": "user", "content": chat["query"]})
                messages.append({"role": "assistant", "content": chat["response"]})
            return messages
        else:
            st.error("Failed to load chat history")
    except Exception as e:
        st.error(f"Failed to load chat history: {e}")
    
    return []

def set_auth(token):
    st.session_state["token"] = token
    st.session_state["authenticated"] = True

def get_headers():
    if st.session_state["token"]:
        return {"Authorization": f"Bearer {st.session_state['token']}"}
    return {}
    
with st.sidebar:
    if not st.session_state["authenticated"]:
        if not st.session_state["show_login"] and not st.session_state["show_register"]:
            login_clicked = st.button("Log in", key="login_btn")
            register_clicked = st.button("Register", key="register_btn")
            if login_clicked:
                st.session_state["show_login"] = True
                st.session_state["show_register"] = False
                st.rerun()

            if register_clicked:
                st.session_state["show_register"] = True
                st.session_state["show_login"] = False
                st.rerun()

        if st.session_state["show_register"]:
            back_clicked = st.button("Back", key="register_back_btn")
            if back_clicked:
                st.session_state["show_register"] = False
                st.session_state["show_login"] = False
                st.rerun()

            with st.form(key="register_form", clear_on_submit=True):
                name = st.text_input("Enter your name")
                password = st.text_input("Enter your password", type="password")
                email = st.text_input("Enter your email")
                submit_button = st.form_submit_button("Submit")
                if submit_button:
                    if not password or not email or not name:
                        st.error("Enter all fields")
                    else:
                        url = f"{API_URL}/register"
                        payload = {"name": name, "password": password, "email": email}
                        response = requests.post(url, json=payload)
                        if response.status_code == 200:
                            st.success("Registered successfully!")
                            st.session_state["show_register"] = False
                            st.session_state["show_login"] = False
                            st.rerun()
                        else:
                            st.error("Registration failed")

        if st.session_state["show_login"] and not st.session_state["show_register"]:
            if st.button("Back"):
                    st.session_state["show_login"] = False
                    st.rerun()
            with st.form(key="login_form", clear_on_submit=True):
                name = st.text_input("Enter your name")
                password = st.text_input("Enter your password", type="password")
                submit_button = st.form_submit_button("Submit")
                if submit_button:
                    if not name or not password:
                        st.error("Complete all fields")
                    else:
                        url = f"{API_URL}/login"
                        payload = {"name": name, "password": password}
                        response = requests.post(url=url, json=payload)
                        if response.status_code == 200:
                            token = response.json()["token"]
                            set_auth(token)
                            st.success("Logged in successfully!")
                            st.session_state["show_login"] = False
                            st.session_state["authenticated"] = True
                            st.rerun()
                        else:
                            st.error("Failed logging in")
    else:
        st.header("Profile")
        url = f"{API_URL}/profile/"
        response = requests.get(url=url, headers=get_headers())
        if response.status_code == 200:
            profile = response.json()
            st.markdown(f"Name: {profile["name"]}")
            st.markdown(f"Email: {profile["email"]}")
            st.markdown(f"Created At: {profile["created_at"]}")

        if st.button("Log out"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["show_login"] = False
            st.session_state["show_register"] = False
            st.rerun()
        
        st.header("Collections")
        response = requests.get(f"{API_URL}/collections/", headers=get_headers())
        if response.status_code == 200:
            collections = response.json()
            if collections:
                for col in collections:
                    st.markdown(f"**ID:** {col['id']} | **Name:** {col['name']} | **Created:** {col['created_at']}")
            else:
                st.info("No collections found. Create one below")
        else:
            st.error("Failed to load collections")
        
        st.header("Create collection")
        collection_name = st.text_input("Collection name", key="collection_create_name")
        if st.button("Create collection"):
            if collection_name.strip():
                payload = {"name": collection_name}
                headers = get_headers()                
                response = requests.post(f"{API_URL}/collections", json=payload, headers=headers)
                
                if response.status_code == 200:
                    st.success("Collection created successfully!")
                    st.rerun()
                else:
                    st.error(f"Failed to create collection")
            else:
                st.error("Please enter a name for the collection")

        
        st.markdown("---")
        st.header("Upload Document")
        uploaded_file = st.file_uploader("")
        collection_id = st.text_input("Collection ID for upload", key="upload_collection_id")
        if uploaded_file and collection_id:
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            params = {"collection_id": collection_id}
            resp = requests.post(f"{API_URL}/documents/upload", files=files, params=params, headers=get_headers())
            if resp.status_code == 200:
                st.success("Document uploaded successfully!")
            else:
                st.error("Failed to upload document")
        
        st.markdown("---")


logo_path = "images/icon.png"
col1, col2, col3, col4 = st.columns([3,5,5,4])
with col1:
    st.image(logo_path, width=200)
with col2:
    st.title("RAGility")
    st.caption("Document based AI assistant")
with col4:
    if st.session_state["authenticated"]:
        query_type = st.radio("Query Type", ["Simple", "Enhanced (Remembers chat history)"])
        chat_collection_id = st.text_input("Collection ID")
with col3:
    if st.session_state["authenticated"]:
        st.subheader("How to use:")
        st.caption("1. Create a collection")
        st.caption("2. Upload a document in the collection")
        st.caption("3. Make a prompt based on a collection of documents")
    
def response_generator(response_text):
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05)
    
if st.session_state["authenticated"]:
    try:
        current_collection_id = int(chat_collection_id) if chat_collection_id else None
    except (ValueError, TypeError):
        current_collection_id = None
    
    if "current_collection" not in st.session_state:
        st.session_state["current_collection"] = None
        
    if current_collection_id and query_type == "Enhanced (Remembers chat history)":
        if st.session_state["current_collection"] != current_collection_id:
            st.session_state["current_collection"] = current_collection_id
            historical_messages = load_chat_history(current_collection_id)
            st.session_state["messages"] = historical_messages
    elif current_collection_id is None or query_type == "Simple":
        if st.session_state.get("current_collection") != "simple":
            st.session_state["current_collection"] = "simple"
            st.session_state["messages"] = []
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Ask something"):
        if not current_collection_id:
            st.error("Please enter a valid Collection ID")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
        
            with st.chat_message("user"):
                st.markdown(prompt)

            payload = {"collection_id": current_collection_id, "query": prompt}
            if query_type == "Simple":
                endpoint = "simple"
            else:
                endpoint = "chat"

            resp = requests.post(f"{API_URL}/query/{endpoint}", json=payload, headers=get_headers())
            if resp.status_code == 200:
                result = resp.json()
                with st.chat_message("assistant"):
                    response = st.write_stream(response_generator(result["response"]))
                st.session_state.messages.append({"role": "assistant", "content": result["response"]})
            else:
                st.error("Failed to get response from AI")
