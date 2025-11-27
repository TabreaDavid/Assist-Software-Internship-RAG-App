import streamlit as st
import time
from typing import List, Dict, Optional
from api_client import APIClient


class RAGilityApp:
    def __init__(self, api_client: APIClient):
        self.api_client = api_client
        self._initialize_session_state()
    
    def _initialize_session_state(self):
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
        
        if "current_collection" not in st.session_state:
            st.session_state["current_collection"] = None
    
    def load_chat_history(self, collection_id: int) -> List[Dict[str, str]]:
        try:
            response = self.api_client.get_chat_history(collection_id, st.session_state["token"])
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
    
    def set_auth(self, token: str):
        st.session_state["token"] = token
        st.session_state["authenticated"] = True
    
    def render_sidebar(self):
        with st.sidebar:
            if not st.session_state["authenticated"]:
                self._render_unauthenticated_sidebar()
            else:
                self._render_authenticated_sidebar()
    
    def _render_unauthenticated_sidebar(self):
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
            self._render_register_form()
        
        if st.session_state["show_login"] and not st.session_state["show_register"]:
            self._render_login_form()
    
    def _render_register_form(self):
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
                    response = self.api_client.register(name, password, email)
                    if response.status_code == 200:
                        st.success("Registered successfully!")
                        st.session_state["show_register"] = False
                        st.session_state["show_login"] = False
                        st.rerun()
                    else:
                        st.error("Registration failed")
    
    def _render_login_form(self):
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
                    response = self.api_client.login(name, password)
                    if response.status_code == 200:
                        token = response.json()["token"]
                        self.set_auth(token)
                        st.success("Logged in successfully!")
                        st.session_state["show_login"] = False
                        st.session_state["authenticated"] = True
                        st.rerun()
                    else:
                        st.error("Failed logging in")
    
    def _render_authenticated_sidebar(self):
        st.header("Profile")
        response = self.api_client.get_profile(st.session_state["token"])
        if response.status_code == 200:
            profile = response.json()
            st.markdown(f"Name: {profile['name']}")
            st.markdown(f"Email: {profile['email']}")
            st.markdown(f"Created At: {profile['created_at']}")
        
        if st.button("Log out"):
            st.session_state["authenticated"] = False
            st.session_state["token"] = None
            st.session_state["show_login"] = False
            st.session_state["show_register"] = False
            st.rerun()
        
        st.header("Collections")
        response = self.api_client.get_collections(st.session_state["token"])
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
                response = self.api_client.create_collection(collection_name, st.session_state["token"])
                if response.status_code == 200:
                    st.success("Collection created successfully!")
                    st.rerun()
                else:
                    st.error("Failed to create collection")
            else:
                st.error("Please enter a name for the collection")
        
        st.markdown("---")
        
        st.header("Upload Document")
        uploaded_file = st.file_uploader("Choose a file", label_visibility="collapsed")
        collection_id = st.text_input("Collection ID for upload", key="upload_collection_id")
        if uploaded_file and collection_id:
            response = self.api_client.upload_document(
                uploaded_file.name, 
                uploaded_file.getvalue(), 
                int(collection_id), 
                st.session_state["token"]
            )
            if response.status_code == 200:
                st.success("Document uploaded successfully!")
            else:
                st.error("Failed to upload document")
        
        st.markdown("---")
    
    def render_header(self, logo_path: str = "images/icon.png") -> tuple:
        col1, col2, col3, col4 = st.columns([3, 5, 5, 4])
        
        with col1:
            st.image(logo_path, width=200)
        
        with col2:
            st.title("RAGility")
            st.caption("Document based AI assistant")
        
        query_type = None
        chat_collection_id = None
        
        if st.session_state["authenticated"]:
            with col4:
                query_type = st.radio("Query Type", ["Simple", "Enhanced (Remembers chat history)"])
                chat_collection_id = st.text_input("Collection ID")
            
            with col3:
                st.subheader("How to use:")
                st.caption("1. Create a collection")
                st.caption("2. Upload a document in the collection")
                st.caption("3. Make a prompt based on a collection of documents")
        
        return query_type, chat_collection_id
    
    def response_generator(self, response_text: str):
        for word in response_text.split():
            yield word + " "
            time.sleep(0.05)
    
    def render_chat_interface(self, query_type: Optional[str], chat_collection_id: Optional[str]):
        if not st.session_state["authenticated"]:
            return
        
        try:
            current_collection_id = int(chat_collection_id) if chat_collection_id else None
        except (ValueError, TypeError):
            current_collection_id = None
        
        if current_collection_id and query_type == "Enhanced (Remembers chat history)":
            if st.session_state["current_collection"] != current_collection_id:
                st.session_state["current_collection"] = current_collection_id
                historical_messages = self.load_chat_history(current_collection_id)
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
                
                if query_type == "Simple":
                    response = self.api_client.query_simple(
                        current_collection_id, 
                        prompt, 
                        st.session_state["token"]
                    )
                else:
                    response = self.api_client.query_chat(
                        current_collection_id, 
                        prompt, 
                        st.session_state["token"]
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    with st.chat_message("assistant"):
                        response_text = st.write_stream(self.response_generator(result["response"]))
                    st.session_state.messages.append({"role": "assistant", "content": result["response"]})
                else:
                    st.error("Failed to get response from AI")
    
    def run(self):
        self.render_sidebar()
        query_type, chat_collection_id = self.render_header()
        self.render_chat_interface(query_type, chat_collection_id)
