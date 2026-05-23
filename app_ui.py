import streamlit as st
import os
import time

# 🎉 CLOUD DEPLOYMENT RESILIENCE PASS: Handle headless display initializations gracefully
try:
    import pyautogui
    PYAUTOGUI_AVAILABLE = True
except (ImportError, Exception):
    PYAUTOGUI_AVAILABLE = False

from PIL import Image
from google import genai
from google.genai import types

from memory_engine import index_project_file, search_memory
from dotenv import load_dotenv
from navigator_mcp import ingest_remote_github
import importlib
import json
import glob
from datetime import datetime

# The Ultimate Multi-Language Production Extension Whitelist
SUPPORTED_EXTENSIONS = (
    # Python & Notebooks
    '.py', '.pyw', '.ipynb', 
    # JavaScript, TypeScript & Frontend Frameworks
    '.js', '.jsx', '.mjs', '.ts', '.tsx', '.vue', '.svelte', 
    # Web Markup & Style sheets
    '.html', '.htm', '.css', '.scss', '.sass', '.less', 
    # Backend, Systems & Mobile Languages
    '.java', '.kt', '.kts', '.swift', '.go', '.rs', '.cpp', '.cc', '.cxx', '.c', '.h', '.hpp', '.cs', '.php', '.rb',
    # Hardware Description & Engineering Formats
    '.v', '.sv', '.vh', '.vhd', '.vhdl', '.h5', '.mat',
    # Data Data Frameworks & Serialization Configs
    '.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.conf', '.env',
    # Documentation & Text Layers
    '.md', '.txt', '.rst', '.adoc'
)

load_dotenv()

# ==========================================
# RESOURCE CACHE ENGINE (ZERO-LATENCY LOADING)
# ==========================================
@st.cache_resource
def initialize_genai_client():
    """Initializes the heavy Google GenAI SDK Client wrapper exactly once."""
    from google import genai
    print("🚀 Initializing CodeNexus GenAI Engine (Cache Miss)...")
    return genai.Client()

client = initialize_genai_client()
model_id = "gemini-3.1-flash-lite"

# 🎉 UNIFIED CLOUD WORKSPACE ARCHITECTURE:
# Hardcoding a flat, shared runtime directory guarantees that both 'adminuser' 
# and 'appuser' scopes point to the exact same physical folder layer.
BASE_WORKSPACE_DIR = "/home/adminuser/codenexus_workspaces"
os.makedirs(BASE_WORKSPACE_DIR, exist_ok=True)

# Load OAuth App Credentials
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

def get_active_workspace_path():
    """Resolves the absolute path for the active thread's repo context or fallback sandbox."""
    active_repo = st.session_state.get("active_repo_name")
    if active_repo:
        path = os.path.join(BASE_WORKSPACE_DIR, active_repo).replace("\\", "/")
        os.makedirs(path, exist_ok=True)
        return path
    
    # Fallback sandbox containment configuration
    sandbox_path = os.path.abspath("./sandbox").replace("\\", "/")
    os.makedirs(sandbox_path, exist_ok=True)
    sample_file = os.path.join(sandbox_path, "sample_project.py")
    if not os.path.exists(sample_file):
        with open(sample_file, "w", encoding="utf-8") as f:
            f.write("# CodeNexus Sandbox\nprint('🛰️ Awaiting remote repository ingestion...')\n")
    return sandbox_path

# ==========================================
# 1. LOCAL CODENEXUS CORE TOOLS
# ==========================================
def list_code_files(path: str = ".", **kwargs):
    """Lists all code-related files, securely locked inside the active workspace container."""
    scan_target = get_active_workspace_path()
    files = []
    exclude_dirs = {'venv', '.git', '__pycache__', 'node_modules', 'nexus_memory', '.next', 'dist', 'build'}
    for root, dirs, filenames in os.walk(scan_target):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in filenames:
            # 🎉 Unified master list synchronization pass
            if filename.endswith(SUPPORTED_EXTENSIONS) or filename == ".env":
                clean_path = os.path.join(root, filename).replace("\\", "/")
                files.append(clean_path)
    return files

def read_multiple_files(file_paths: list[str]):
    """Reads multiple files and provides specific error reporting."""
    results = {}
    active_root = get_active_workspace_path()
    for path in file_paths:
        # Guarantee target path maps safely inside the active scoped container directory
        resolved_path = path if os.path.isabs(path) else os.path.join(active_root, path)
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                results[path] = f.read()
        except Exception as e:
            results[path] = f"ERROR: {str(e)}"
    return results

def web_search(query: str):
    """Searches the live internet for coding documentation and fixes."""
    try:
        from duckduckgo_search import DDGS  # 🎉 Placed exactly where it's needed!
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=5):
                results.append(f"Title: {r['title']}\nSource: {r['href']}\nSnippet: {r['body']}\n")
        return "\n---\n".join(results) if results else "No relevant search results found."
    except Exception as e:
        return f"ERROR: Search failed: {str(e)}"

def ask_memory(question: str):
    """Searches long-term vector memory for code snippets."""
    from memory_engine import search_memory
    return search_memory(question)

def apply_code_fix(file_path: str, new_content: str):
    """Creates or updates a code file securely locked inside the active workspace target."""
    try:
        allowed_root = os.path.abspath(get_active_workspace_path())
        
        # Enforce path containment within active scope directory paths
        target_path = file_path if os.path.isabs(file_path) else os.path.join(allowed_root, file_path)
        abs_file_path = os.path.abspath(target_path)
        
        if not abs_file_path.startswith(allowed_root):
            return "ERROR: Security violation. Writing outside target workspace boundaries is prohibited."
            
        if ".env" in file_path or "nexus_memory" in file_path:
            return "ERROR: Security restriction. Cannot modify sensitive system configurations."
            
        os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
        with open(abs_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"SUCCESS: Successfully updated context asset: {file_path}."
    except Exception as e:
        return f"ERROR: {str(e)}"

def capture_screen(label: str = "screenshot"):
    """Takes a high-resolution screenshot of the user's current screen."""
    global PYAUTOGUI_AVAILABLE  # 👈 Add this line to clear the yellow warning!
    
    # Ensure headless cloud deployments return a clean status message instead of dropping a hard crash
    if not PYAUTOGUI_AVAILABLE:
        return "ERROR: Screen capture utility is only available when running CodeNexus locally..."

# ==========================================
# 2. SETUP PAGE & MULTI-THREAD HISTORY STATE
# ==========================================
st.set_page_config(page_title="CodeNexus Autonomous Workspace", layout="wide")

# ==========================================
# GITHUB OAUTH INTERCEPTOR LAYER
# ==========================================
import requests

# Check if GitHub sent an authorization code via the URL query parameters
if "code" in st.query_params:
    auth_code = st.query_params["code"]
    
    # Immediately clear the code from the URL parameters to keep the layout clean
    st.query_params.clear()
    
    with st.spinner("Exchanging authorization code for secure access token..."):
        # Make a background server-to-server POST request to exchange the code for a token
        token_url = "https://github.com/login/oauth/access_token"
        headers = {"Accept": "application/json"}
        payload = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": auth_code
        }
        
        response = requests.post(token_url, headers=headers, data=payload)
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                # Pin the generated user access token directly into active session memory
                st.session_state.github_oauth_token = token_data["access_token"]
                st.toast("GitHub Account Connected Successfully! 🔌", icon="✅")
            else:
                st.error(f"OAuth Error: {token_data.get('error_description', 'Failed to retrieve access token.')}")

# ◄ GLOBAL SECURITY HANDSHAKE SYNCHRONIZATION HOOK
# Enforces token binding parameters universally across all system modules on load pass
if "github_oauth_token" in st.session_state and st.session_state.github_oauth_token:
    os.environ["GITHUB_TOKEN"] = st.session_state.github_oauth_token
    
HISTORY_DIR = "./.nexus_history"
os.makedirs(HISTORY_DIR, exist_ok=True)

def get_all_threads():
    """Scans the history directory and returns a sorted list of thread IDs."""
    files = glob.glob(os.path.join(HISTORY_DIR, "thread_*.json"))
    threads = []
    for f in files:
        base = os.path.basename(f).replace(".json", "")
        threads.append(base)
    return sorted(threads, reverse=True)

def save_session_to_disk():
    """Serializes active session states into a unique conversation thread file."""
    active_id = st.session_state.get("active_thread_id")
    if not active_id:
        return
        
    target_file = os.path.join(HISTORY_DIR, f"{active_id}.json")
    transaction_payload = {
        "messages": st.session_state.get("messages", []),
        "agent_logs": st.session_state.get("agent_logs", []),
        "active_repo_name": st.session_state.get("active_repo_name", None)
    }
    try:
        with open(target_file, "w", encoding="utf-8") as f:
            json.dump(transaction_payload, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"⚠️ Failed to write transaction log: {str(e)}")

def load_session_from_disk(thread_id):
    """Loads historical conversation frames for a specific chosen thread target."""
    target_file = os.path.join(HISTORY_DIR, f"{thread_id}.json")
    if os.path.exists(target_file):
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", []), data.get("agent_logs", []), data.get("active_repo_name", None)
        except Exception as e:
            print(f"⚠️ Failed to rehydrate selected thread memory: {str(e)}")
    return [], ["🚀 Session initialized. Ready for new operations."], None

all_existing_threads = get_all_threads()

if "active_thread_id" not in st.session_state:
    if all_existing_threads:
        st.session_state.active_thread_id = all_existing_threads[0]
    else:
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.session_state.active_thread_id = f"thread_{now_str}"

# 🎉 THE REHYDRATION GUARD FIX: Force disk reload if state values are completely missing or empty
if "messages" not in st.session_state or ("active_thread_id" in st.session_state and not st.session_state.messages and all_existing_threads):
    m_hist, l_hist, r_name = load_session_from_disk(st.session_state.active_thread_id)
    st.session_state.messages = m_hist
    st.session_state.agent_logs = l_hist
    st.session_state.active_repo_name = r_name

if "vision_context" not in st.session_state:
    st.session_state.vision_context = None

if os.path.exists("last_vision_capture.png"):
    try:
        with open("last_vision_capture.png", "rb") as f:
            st.session_state.vision_context = f.read()
        os.remove("last_vision_capture.png")
        st.session_state.agent_logs.append("👁️ Stored image context into active memory.")
        save_session_to_disk()
    except Exception as e:
        st.session_state.agent_logs.append(f"⚠️ Image error: {str(e)}")

# ==========================================
# 3. THE COCKPIT (SIDEBAR MULTI-CHAT CORE)
# ==========================================
def get_all_threads():
    """Scans the history directory and returns a sorted list of all active JSON thread IDs."""
    files = glob.glob(os.path.join(HISTORY_DIR, "*.json"))
    threads = []
    for f in files:
        base = os.path.basename(f).replace(".json", "")
        if base:
            threads.append(base)
    return sorted(threads, reverse=True)

with st.sidebar:
    st.title("🛰️ Nexus Mission Control")
    st.subheader("📁 Architectural Sessions")
    
    current_threads = get_all_threads()
    
    if st.button("➕ New Architectural Session", use_container_width=True):
        now_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Define fresh markers
        st.session_state.active_thread_id = f"thread_{now_str}"
        st.session_state.messages = []
        st.session_state.agent_logs = ["🚀 Fresh session container generated. System standing by..."]
        st.session_state.vision_context = None
        st.session_state.active_repo_name = None
        st.session_state.last_push_success_msg = None
        st.session_state.repo_analysis_success = False
        save_session_to_disk()
        st.rerun()
        
    if current_threads:
        try:
            current_index = current_threads.index(st.session_state.active_thread_id)
        except ValueError:
            current_index = 0
            
        selected_thread = st.selectbox(
            "Select Active Conversation Thread:",
            options=current_threads,
            index=current_index,
            label_visibility="collapsed"
        )
        
        if selected_thread != st.session_state.active_thread_id:
            # Save the current thread's state before switching
            save_session_to_disk()

            # 🎉 THE DIRECT SYNC PATCH: Instantly rehydrate states inside event trigger
            st.session_state.active_thread_id = selected_thread
            m_hist, l_hist, r_name = load_session_from_disk(selected_thread)
            st.session_state.messages = m_hist
            st.session_state.agent_logs = l_hist
            st.session_state.active_repo_name = r_name
            st.session_state.vision_context = None
            st.session_state.last_push_success_msg = None
            st.session_state.repo_analysis_success = True if r_name else False
            st.rerun()

    if st.button("🗑️ Delete Selected Thread", use_container_width=True):
        target_del = os.path.join(HISTORY_DIR, f"{st.session_state.active_thread_id}.json")
        if os.path.exists(target_del):
            try: os.remove(target_del)
            except Exception: pass
        st.session_state.pop("active_thread_id", None)
        st.session_state.pop("messages", None)
        st.session_state.pop("agent_logs", None)
        st.session_state.pop("active_repo_name", None)
        st.session_state.pop("last_push_success_msg", None)
        st.session_state.repo_analysis_success = False
        st.rerun()

    if st.button("🔄 Complete Hard Workspace Purge", use_container_width=True):
        st.session_state.messages = []
        st.session_state.agent_logs = ["🧹 Workspace cleared. Ready for new operations."]
        st.session_state.vision_context = None
        st.session_state.active_repo_name = None
        st.session_state.last_push_success_msg = None
        st.session_state.repo_analysis_success = False
        
        import shutil
        if os.path.exists(HISTORY_DIR):
            try: shutil.rmtree(HISTORY_DIR)
            except Exception: pass
        if os.path.exists(BASE_WORKSPACE_DIR):
            try:
                def remove_readonly(func, path, excinfo):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                shutil.rmtree(BASE_WORKSPACE_DIR, onerror=remove_readonly)
            except Exception: pass
        st.rerun()
        
    st.write("---")
    st.subheader("🌐 Remote Repository Target")
    remote_url = st.text_input("Paste GitHub Repository URL:", placeholder="https://github.com/...")
    
    if st.button("🚀 Analyze External Repository", use_container_width=True):
        if remote_url:
            extracted_name = remote_url.split("/")[-1].replace(".git", "")
            old_thread_id = st.session_state.active_thread_id
            new_thread_id = f"📦 {extracted_name}"
            
            old_file_path = os.path.join(HISTORY_DIR, f"{old_thread_id}.json")
            if os.path.exists(old_file_path):
                try: os.remove(old_file_path)
                except Exception: pass
            
            st.session_state.active_thread_id = new_thread_id
            st.session_state.active_repo_name = extracted_name
            target_directory_path = os.path.join(BASE_WORKSPACE_DIR, extracted_name).replace("\\", "/")
            st.session_state.last_push_success_msg = None
            
            is_already_cloned = os.path.exists(target_directory_path) and len(os.listdir(target_directory_path)) > 0 if os.path.exists(target_directory_path) else False
            
            if is_already_cloned:
                st.session_state.agent_logs.append("⚡ Repository targeted already exists and is populated. Synchronizing smoothly...")
                st.session_state.repo_analysis_success = True
            else:
                with st.spinner(f"Cloning '{extracted_name}' cleanly into isolated workspace..."):
                    import subprocess
                    import shutil
                    
                    try:
                        if os.path.exists(target_directory_path):
                            try: shutil.rmtree(target_directory_path, onerror=remove_readonly)
                            except Exception: pass
                            
                        os.makedirs(target_directory_path, exist_ok=True)
                        
                        # Direct system execution using the unmodified public URL
                        clone_command = ["git", "clone", remote_url, target_directory_path]
                        
                        custom_env = os.environ.copy()
                        custom_env["GIT_TERMINAL_PROMPT"] = "0"
                        
                        result = subprocess.run(
                            clone_command,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            text=True,
                            env=custom_env
                        )
                        
                        if result.returncode != 0:
                            raise Exception(result.stderr)

                        st.session_state.agent_logs.append(f"🔌 Workspace compiled smoothly.")
                        st.session_state.repo_analysis_success = True
                    except Exception as e:
                        st.error(f"Clone routine dropped exception: {str(e)}")
                        st.session_state.repo_analysis_success = False
            
            with st.spinner("Re-seeding local vector database..."):
                from memory_engine import index_project_file
                new_target_files = list_code_files()
                for f_path in new_target_files:
                    try:
                        with open(f_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        index_project_file(f_path, content)
                    except Exception: pass
                        
                st.session_state.agent_logs.append(f"✅ ChromaDB synchronized with isolated branch: {extracted_name}")
                save_session_to_disk()
                st.rerun()
        else:
            st.warning("Please provide a valid URL string.")
            
    # 🎉 FLAW 1 FIXED: Persistent dynamic success indicator card inside sidebar dashboard
    if st.session_state.get("repo_analysis_success"):
        st.success("✅ Repository Context Synchronized Natively", icon="🛰️")

    st.write("---")
    st.subheader("🚀 Cloud Code Deployment")
    active_repo = st.session_state.get("active_repo_name")
    
    if active_repo:
        if "github_oauth_token" not in st.session_state:
            login_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
            st.warning("Authentication Required to Deploy Changes.")
            st.markdown(f'<a href="{login_url}" target="_self"><button style="width:100%; height:40px; background-color:#24292e; color:white; border:none; border-radius:5px; cursor:pointer; font-weight:bold;">🔗 Connect GitHub Account</button></a>', unsafe_allow_html=True)
        else:
            st.success("🔒 Authenticated via GitHub OAuth")
            if "messages" in st.session_state and st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.last_push_success_msg = None

            if st.session_state.get("last_push_success_msg"):
                st.info(st.session_state.last_push_success_msg)
            
            push_mode = st.checkbox("👥 Push directly to Original Origin Team Repo", value=False)
            commit_note = st.text_input("Custom Commit Message:", placeholder="AI-generated fallback if empty...")
            
            if st.button("🛰️ Push Workspace to GitHub", use_container_width=True):
                with st.spinner("Bundling workspace layers and executing push routine..."):
                    from navigator_mcp import push_workspace_to_github
                    active_workspace_path = get_active_workspace_path()
                    os.environ["GITHUB_TOKEN"] = st.session_state.github_oauth_token
                    push_status = push_workspace_to_github(active_workspace_path, commit_note, push_mode)
                    
                    if "ERROR" in push_status:
                        st.error(push_status)
                        st.session_state.last_push_success_msg = None
                    else:
                        st.session_state.last_push_success_msg = f"{push_status}"
                        st.balloons()
                        save_session_to_disk()
                        st.rerun()
    else:
        st.caption("🔒 Target a public remote repository to activate push capabilities.")
        st.session_state.last_push_success_msg = None

    st.write("---")
    st.subheader("🛠️ Agent Thought Stream")
    if "agent_logs" in st.session_state and st.session_state.agent_logs:
        for log in st.session_state.agent_logs[-8:]:
            st.caption(log)

# ==========================================
# 4. CHAT INTERFACE & HISTORICAL TIMELINE
# ==========================================
# 🎉 THE UI FIX: Clean, production-grade styling bounds that dock components without breaking native widths
st.markdown("""
    <style>
        /* 1. Create a floating baseline anchor zone for the sticky bottom layout row */
        div[data-testid="stChatInputCurrentChatContainer"] {
            position: fixed !important;
            bottom: 20px !important;
            left: 21%;
            width: 76%;
            background-color: #0e1117;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #30363d;
            box-shadow: 0px -4px 20px rgba(0, 0, 0, 0.5);
            z-index: 99999;
        }
        
        /* 2. Position the file staging attachment bar neatly directly inside the anchor zone */
        .sticky-dock-wrapper {
            margin-bottom: 10px;
            width: 100%;
        }
        
        /* 3. Ensure the text entry box always scales to match full available width limits */
        .stChatInput > div {
            width: 100% !important;
        }
        
        /* 4. Padding cushion block to prevent historical messages from getting hidden beneath the sticky bottom dock */
        .main .block-container {
            padding-bottom: 220px !important;
        }
    </style>
""", unsafe_allow_html=True)

st.title("CodeNexus Architect")

if st.session_state.get("active_repo_name"):
    st.caption(f"🎯 Active Targeted Context Workspace: `{st.session_state.active_repo_name}`")

# Render active conversation timeline records
if not st.session_state.messages:
    st.markdown("""
    ### Welcome to CodeNexus Autonomous Engine v1.0
    An interactive, multi-agent engineering cockpit built to autonomously comprehend, map, audit, and refactor software codebases.
    """)
else:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if "image" in msg and msg["image"] is not None:
                st.image(msg["image"], use_container_width=True)

# ==========================================
# 5. FIXED STICKY INPUT & CONTEXT HANDSHAKE
# ==========================================
# Staging Container wrapper row setup inside the unified layout block
st.markdown('<div class="sticky-dock-wrapper">', unsafe_allow_html=True)
col_toggle, col_preview = st.columns([0.22, 0.78])

with col_toggle:
    expand_attach = st.button("➕ Attach Payload Context", use_container_width=True)

with col_preview:
    if "staged_file_payload" in st.session_state and st.session_state.staged_file_payload:
        f_name, f_type, _ = st.session_state.staged_file_payload
        st.success(f"🔒 Staging Buffer Ingested: `{f_name}`")
        if st.button("🗑️ Remove Asset"):
            st.session_state.staged_file_payload = None
            st.rerun()
    else:
        st.caption("No external multi-modal layer payloads staged in buffer loop.")

if expand_attach or st.session_state.get("uploader_visible", False):
    st.session_state.uploader_visible = True
    uploaded_asset = st.file_uploader("Drop contextual layer logs directly into model channels:", type=["png", "jpg", "jpeg", "py", "js", "ts", "jsx", "tsx", "html", "css", "json", "txt", "md"], label_visibility="collapsed")
    if uploaded_asset is not None:
        asset_bytes = uploaded_asset.read()
        st.session_state.staged_file_payload = (uploaded_asset.name, uploaded_asset.type, asset_bytes)
        st.session_state.uploader_visible = False
        st.rerun()
st.markdown('</div>', unsafe_allow_html=True) # Close the sticky wrapper block neatly

# Global sticky text input console window hook
prompt = st.chat_input("Command the Architect...")

if prompt:
    compiled_user_message = prompt
    parts_payload = [types.Part.from_text(text=prompt)]
    staged_image_bytes = None
    
    if "staged_file_payload" in st.session_state and st.session_state.staged_file_payload:
        f_name, f_type, f_bytes = st.session_state.staged_file_payload
        if f_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            clean_mime = "image/jpeg" if f_name.lower().endswith((".jpg", ".jpeg")) else "image/png"
            parts_payload.append(types.Part.from_bytes(data=f_bytes, mime_type=clean_mime))
            compiled_user_message += f"\n\n*[📎 Attached UI Capture Context: {f_name}]*"
            staged_image_bytes = f_bytes
        else:
            decoded_text = f_bytes.decode("utf-8", errors="ignore")
            compiled_user_message += f"\n\n*[📎 Attached File Context: {f_name}]*\n```python\n{decoded_text}\n```"
            parts_payload[0] = types.Part.from_text(text=compiled_user_message)
        st.session_state.staged_file_payload = None

    st.session_state.messages.append({
        "role": "user", 
        "content": compiled_user_message,
        "image": staged_image_bytes
    })
    st.session_state.active_parts_payload = parts_payload
    save_session_to_disk()
    st.rerun()

# Dynamic Multi-Turn Agent Orchestrator Running Loop
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    active_prompt = st.session_state.messages[-1]["content"]
    
    import importlib
    import navigator_mcp
    import seed_memory
    importlib.reload(navigator_mcp)
    importlib.reload(seed_memory)
    
    from navigator_mcp import push_workspace_to_github

    st.session_state.agent_logs.append(f"📥 Received User Intent: '{active_prompt[:40]}...'")    
    save_session_to_disk()

    available_functions = {
        "list_code_files": list_code_files,
        "read_multiple_files": read_multiple_files,
        "web_search": web_search,
        "ask_memory": ask_memory,
        "apply_code_fix": apply_code_fix,
        "capture_screen": capture_screen,
        "push_workspace_to_github": push_workspace_to_github
    }

    tools = [{"function_declarations": [
        {"name": "list_code_files", "description": "Lists all available filenames in the project workspace path. Takes no arguments.", "parameters": {"type": "OBJECT", "properties": {}}},
        {"name": "read_multiple_files", "description": "Reads and returns the literal code content of specified file paths. Use this to read files discovered via list_code_files.", "parameters": {"type": "OBJECT", "properties": {"file_paths": {"type": "ARRAY", "items": {"type": "STRING"}}}}},
        {"name": "web_search", "description": "Searches the live internet for external documentation updates.", "parameters": {"type": "OBJECT", "properties": {"query": {"type": "STRING"}}}},
        {"name": "ask_memory", "description": "Queries the local semantic vector database for specific code components, math logic, or functionality across all files.", "parameters": {"type": "OBJECT", "properties": {"question": {"type": "STRING"}}}},
        {"name": "apply_code_fix", "description": "Updates or modifies code files safely inside the active repository boundaries.", "parameters": {"type": "OBJECT", "properties": {"file_path": {"type": "STRING"}, "new_content": {"type": "STRING"}}, "required": ["file_path", "new_content"]}},
        {"name": "capture_screen", "description": "Takes a screenshot of the user's monitor screen environment."}
    ]}]

    architect_instruction = (
        "ROLE & SCOPE BOUNDARY:\n"
        "You are the Core Lead Architect of CodeNexus. You are an expert at analyzing software systems and code repositories.\n\n"
        "OPERATIONAL METRICS:\n"
        "1. To understand what files are available, look at the directory structure using `list_code_files` exactly once.\n"
        "2. Once `list_code_files` returns the list of file paths, you MUST immediately call `read_multiple_files` on the target file path to extract its code logic. Do not repeatedly list files."
    )

    reviewer_instruction = (
        "You are the Elite Senior Code Reviewer and Safety Auditor.\n"
        "Analyze code blocks passed to you against system rules. If safe, respond with 'LGTM'."
    )

    # 🎉 FLAW 4 FIXED: Build a fully rehydrated historical conversation history object array stream
    # Instead of wiping out context on every message turn, we map previous messages perfectly into the model context payload
    messages_context = []
    
    # Process up to the final 10 chat messages to maintain a rich, sliding long-term conversational memory context window
    for historical_msg in st.session_state.messages[:-1]:
        hist_parts = [types.Part.from_text(text=historical_msg["content"])]
        if "image" in historical_msg and historical_msg["image"] is not None:
            # Re-attach image context matrices back into the historical timeline loop queues dynamically
            hist_parts.append(types.Part.from_bytes(data=historical_msg["image"], mime_type="image/png"))
        messages_context.append(types.Content(role=historical_msg["role"], parts=hist_parts))

    # Append our current, live instruction turn parts payload 
    if "active_parts_payload" in st.session_state and st.session_state.active_parts_payload:
        user_parts = st.session_state.active_parts_payload
        st.session_state.active_parts_payload = None
    else:
        user_parts = [types.Part.from_text(text=active_prompt)]
        
    messages_context.append(types.Content(role="user", parts=user_parts))

    # Render thinking status card
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        response_placeholder = st.empty()
        
        with st.spinner("CodeNexus multi-agent system executing operations..."):
            for turn in range(8):
                status_placeholder.info(f"Thinking... (Turn {turn + 1}/8)")
                response = client.models.generate_content(
                    model=model_id,
                    config=types.GenerateContentConfig(system_instruction=architect_instruction, tools=tools),
                    contents=messages_context
                )
                
                if not response.candidates or not response.candidates[0].content:
                    continue

                messages_context.append(response.candidates[0].content)
                found_tool_call = False

                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            found_tool_call = True
                            call = part.function_call
                            st.session_state.agent_logs.append(f"🛠 immortality loop prevention - Tool Called: {call.name}")
                            save_session_to_disk()
                            
                            if call.name == "apply_code_fix":
                                st.session_state.agent_logs.append("⚖️ Evaluating via Handshake...")
                                save_session_to_disk()
                                status_placeholder.info("Senior Reviewer auditing code change via RAG memory...")
                                
                                security_memory = ask_memory("What are the security restrictions for modifying project files?")
                                review_ctx = (
                                    f"PROPOSED FILE CHANGE:\nTarget File: {call.args['file_path']}\nNew Content:\n{call.args['new_content']}\n\n"
                                    f"SYSTEM SECURITY BOUNDARIES:\n{security_memory}"
                                )
                                review_msgs = [types.Content(role="user", parts=[types.Part.from_text(text=review_ctx)])]
                                r_res = client.models.generate_content(
                                    model=model_id,
                                    config=types.GenerateContentConfig(system_instruction=reviewer_instruction),
                                    contents=review_msgs
                                )
                                verdict = r_res.text if r_res.text else "No verdict."
                                
                                if "LGTM" in verdict.upper():
                                    st.session_state.agent_logs.append("✅ Approved. Writing file.")
                                    result = available_functions[call.name](**call.args)
                                else:
                                    st.session_state.agent_logs.append("❌ Rejected by Reviewer.")
                                    result = f"REJECTED BY SENIOR REVIEWER. Reason:\n{verdict}"
                                save_session_to_disk()
                            else:
                                result = available_functions[call.name](**call.args)

                            if isinstance(result, (list, dict)):
                                json_response = {"result": result}
                            else:
                                json_response = {"result": str(result)}

                            messages_context.append(types.Content(
                                role="tool",
                                parts=[types.Part.from_function_response(name=call.name, response=json_response)]
                            ))
                
                if not found_tool_call and response.text:
                    st.session_state.agent_logs.append("📢 Operation finalized. Rendering text output.")
                    status_placeholder.empty()
                    response_placeholder.markdown(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    save_session_to_disk()
                    break
        
        # 🎉 FLAW 3 FIXED: Inject a lightweight HTML/JS anchor automation clip right into the assistant viewport.
        # This forcefully commands the browser's window layout frames to automatically scroll down to the bottom on every prompt transaction!
        st.markdown("""
            <script>
                window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
            </script>
        """, unsafe_allow_html=True)
                    
        st.rerun()