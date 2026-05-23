import os

from memory_engine import index_project_file, search_memory
from duckduckgo_search import DDGS
import pyautogui
from PIL import Image
import shutil
from git import Repo
import stat
from datetime import datetime
import requests
import time

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

# ==========================================
# CENTRALIZED PRODUCTION PATH SCHEMAS
# ==========================================
HOME_DIR = os.path.expanduser("~")
BASE_WORKSPACE_DIR = os.path.join(HOME_DIR, "codenexus_workspaces").replace("\\", "/")
SANDBOX_DIR = os.path.abspath("./sandbox").replace("\\", "/")

def list_code_files(path: str = "."):
    """Lists all code-related assets securely locked inside the active context workspace."""
    import streamlit as st
    active_repo = st.session_state.get("active_repo_name")
    
    if active_repo:
        scan_target = os.path.join(BASE_WORKSPACE_DIR, active_repo).replace("\\", "/")
    else:
        scan_target = SANDBOX_DIR
        
    if not os.path.exists(scan_target):
        os.makedirs(scan_target, exist_ok=True)

    files = []
    exclude_dirs = {'venv', '.git', '__pycache__', 'node_modules', 'nexus_memory', '.next', 'dist', 'build'}
    for root, dirs, filenames in os.walk(scan_target):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in filenames:
            # 🎉 Synced directly to match your frontend repository rules
            if filename.endswith(SUPPORTED_EXTENSIONS) or filename == ".env":
                clean_path = os.path.join(root, filename).replace("\\", "/")
                files.append(clean_path)
    return files


def read_multiple_files(file_paths: list[str]):
    """Reads multiple files and provides specific error reporting for better AI reasoning.
    
    Returns a dictionary where keys are file paths and values are file contents or error messages.
    """
    results = {}
    for path in file_paths:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                results[path] = f.read()
        except FileNotFoundError:
            results[path] = f"ERROR: File not found at {path}. Check the path and try again."
        except PermissionError:
            results[path] = f"ERROR: Permission denied for {path}. System access restricted."
        except UnicodeDecodeError:
            results[path] = f"ERROR: {path} is likely a binary file or uses wrong encoding. Cannot read text."
        except Exception as e:
            results[path] = f"ERROR: Unexpected issue: {str(e)}"
    return results


def write_doc_file(filename: str, content: str):
    """Writes architectural documentation or README files to the project.
    
    Only supports writing .md (Markdown) files to prevent accidental overwrites of code.
    """
    try:
        if not filename.endswith('.md'):
            return "ERROR: This tool only supports writing .md (Markdown) documentation files."
            
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully created/updated {filename}"
    except Exception as e:
        return f"ERROR: Could not write file: {str(e)}"
    

def index_everything():
    """Indexes all code files inside the operational scratchpad directory into vector memory."""
    # CHANGED: Left empty to inherit default sandboxed environment routes cleanly
    files = list_code_files() 
    
    status_reports = []
    for f_path in files:
        try:
            with open(f_path, 'r', encoding='utf-8') as f:
                content = f.read()
                report = index_project_file(f_path, content)
                status_reports.append(report)
        except Exception as e:
            status_reports.append(f"Failed to index {f_path}: {e}")
            
    return "\n".join(status_reports)


def ask_memory(question: str):
    """Searches long-term memory to find relevant code snippets and logic for a given question.
    """
    return search_memory(question)


def apply_code_fix(file_path: str, new_content: str):
    """Creates a new code file or updates an existing one safely within active repository limits."""
    import streamlit as st
    try:
        active_repo = st.session_state.get("active_repo_name")
        allowed_root = os.path.abspath(os.path.join(BASE_WORKSPACE_DIR, active_repo) if active_repo else SANDBOX_DIR)
        
        target_path = file_path if os.path.isabs(file_path) else os.path.join(allowed_root, file_path)
        abs_file_path = os.path.abspath(target_path)

        if not abs_file_path.startswith(allowed_root):
            return f"ERROR: Security violation. Attempted to write outside of project boundaries: {file_path}"

        if ".env" in file_path or "nexus_memory" in file_path:
            return "ERROR: Security restriction. Cannot modify sensitive system files."
            
        os.makedirs(os.path.dirname(abs_file_path), exist_ok=True)
        with open(abs_file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"SUCCESS: Successfully updated {file_path}."
    except Exception as e:
        return f"ERROR: Failed to apply fix: {str(e)}"


def web_search(query: str):
    """Searches the live internet for coding documentation, 2026 library updates, and error fixes.
    Returns the top 5 relevant search results with snippets.
    """
    try:
        results = []
        with DDGS() as ddgs:
            # We fetch top 5 results for a balance of speed and context
            for r in ddgs.text(query, max_results=5):
                results.append(f"Title: {r['title']}\nSource: {r['href']}\nSnippet: {r['body']}\n")
        
        if not results:
            return "No relevant search results found."
        return "\n---\n".join(results)
    except Exception as e:
        return f"ERROR: Search failed: {str(e)}"


def capture_screen(label: str = "screenshot"):
    """Takes a high-resolution screenshot of the user's current screen.
    Use this to see terminal errors, UI bugs, or code formatting in VS Code.
    The image is saved locally as 'last_vision_capture.png'.
    """
    try:
        # Capture the entire primary monitor
        screenshot = pyautogui.screenshot()
        
        # Save it to the project root
        file_path = "last_vision_capture.png"
        screenshot.save(file_path)
        
        return f"SUCCESS: Screenshot captured and saved as {file_path}. Label: {label}"
    except Exception as e:
        return f"ERROR: Failed to capture screen: {str(e)}"


def create_new_file(file_path: str, content: str):
    """Creates a new file with the specified content."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"SUCCESS: Created {file_path}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def remove_readonly(func, path, excinfo):
    """Clear the read-only bit on Windows so files can be deleted successfully."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def ingest_remote_github(repo_url: str) -> str:
    """Clones a remote GitHub repository to the isolated system workspaces directory."""
    extracted_name = repo_url.split("/")[-1].replace(".git", "")
    target_directory_path = os.path.join(BASE_WORKSPACE_DIR, extracted_name).replace("\\", "/")
    
    if os.path.exists(target_directory_path):
        try:
            shutil.rmtree(target_directory_path, onerror=remove_readonly)
        except Exception as e:
            return f"ERROR: Failed to clean workspace: {str(e)}"
            
    try:
        os.makedirs(target_directory_path, exist_ok=True)
        Repo.clone_from(repo_url, target_directory_path)
        return "SUCCESS"
    except Exception as e:
        return f"ERROR: Failed to clone repository. Reason: {str(e)}"
    

# =========================================================================
# UPGRADED AUTONOMOUS OAUTH DEPLOYMENT ROUTINE WITH AUTOMATED REPO CREATION
# =========================================================================
def push_workspace_to_github(repo_path: str, commit_message: str = None, push_to_origin: bool = False) -> str:
    """Stages, commits, and deploys workspace code layers. 
    
    Autonomously provisions target repositories via GitHub API if they do not exist, 
    and handles group project overrides seamlessly.
    """
    try:
        if not os.path.exists(repo_path):
            return "ERROR: Active workspace path does not exist on disk."
            
        repo = Repo(repo_path)
        github_token = os.environ.get("GITHUB_TOKEN")
        
        if not github_token:
            return "ERROR: Missing valid OAuth authentication token."

        origin = repo.remote(name='origin')
        original_url = origin.url
        repo_name = original_url.split("/")[-1].replace(".git", "")

        # Stage and commit any outstanding changes
        if repo.is_dirty(untracked_files=True):
            repo.git.add(A=True)
            if not commit_message or commit_message.strip() == "":
                commit_message = f"CodeNexus Automated Refactor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            repo.git.commit('-m', commit_message)

        active_branch = repo.active_branch.name

        # GROUP DEPLOYMENT ROUTINE: Push directly back to the original source location
        if push_to_origin:
            print(f"👥 Collaborative push requested to team origin path: {original_url}")
            authenticated_url = original_url.replace("https://github.com/", f"https://{github_token}@github.com/")
            origin.set_url(authenticated_url)
            origin.push(refspec=f"{active_branch}:{active_branch}")
            origin.set_url(original_url)
            return f"SUCCESS: Multi-collaborator modifications deployed cleanly to team repository origin!"

        # INDEPENDENT ROUTINE: Resolve personal user profile pathways
        profile_url = "https://api.github.com/user"
        profile_headers = {"Authorization": f"token {github_token}"}
        profile_res = requests.get(profile_url, headers=profile_headers)
        
        if profile_res.status_code == 200:
            username = profile_res.json().get("login")
        else:
            return "ERROR: Failed to resolve authenticated user identity via OAuth token."

        personal_repo_url = f"https://github.com/{username}/{repo_name}"
        origin.set_url(personal_repo_url)

        authenticated_url = personal_repo_url.replace("https://github.com/", f"https://{github_token}@github.com/")
        origin.set_url(authenticated_url)

        try:
            origin.push(refspec=f"{active_branch}:{active_branch}")
            origin.set_url(personal_repo_url)
            return f"SUCCESS: Modifications successfully deployed to your personal repository branch!"
            
        except Exception as git_err:
            # INTERCEPT 404/NOT FOUND ERRORS NATIVELY
            if "not found" in str(git_err).lower() or "404" in str(git_err):
                print(f"🔨 Repository '{repo_name}' not found on profile. Provisioning new cloud repository...")
                
                create_repo_url = "https://api.github.com/user/repos"
                create_payload = {
                    "name": repo_name,
                    "description": "Autonomously generated and refactored via CodeNexus Intelligence Cockpit.",
                    "private": False,
                    "has_issues": True,
                    "has_projects": True,
                    "has_wiki": True
                }
                
                create_res = requests.post(create_repo_url, headers=profile_headers, json=create_payload)
                
                if create_res.status_code == 201:
                    print("🚀 Cloud repository successfully initialized! Executing payload sync...")
                    time.sleep(2) # Prevent Git race conditions
                    origin.push(refspec=f"{active_branch}:{active_branch}")
                    origin.set_url(personal_repo_url)
                    return f"SUCCESS: Cloud repository initialized autonomously! Workspace successfully pushed to your profile."
                else:
                    origin.set_url(personal_repo_url)
                    return f"ERROR: Automated repository creation failed: {create_res.json().get('message')}"
            raise git_err
            
    except Exception as e:
        return f"ERROR: Git deployment automation dropped an exception: {str(e)}"