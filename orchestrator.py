# Import the actual functions from your Day 1 script
# use the tool apply_code_fix on memory_engine.py. Replace the slice_code function with a standard def version donot rename the function. keep the name as slice_code. use the tool apply_code_fix to update memory_engine.py with this exact logic def slice_code(content): chunks = re.split(r'\n(?=async def |def |class)',content) return [c.strip() for c in chunks if c.strip()] donot add any other text or changes
#I saw the Reviewer's audit. I agree. Architect, please update navigator_mcp.py to Add the print statement to list_code_files. Fix the apply_code_fix security check to use os.path.basename as the Reviewer suggested.
from navigator_mcp import (
            list_code_files, 
            read_multiple_files, 
            write_doc_file, 
            index_everything, 
            ask_memory,
            apply_code_fix,
            web_search,
            capture_screen,
            create_new_file
        )
import os
import sys # Added to handle forced output
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Load the API Key
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

print("--- Initializing CodeNexus Brain ---", flush=True)

try:
    client = genai.Client(api_key=api_key)
    model_id = "gemini-3.1-flash-lite"

    system_instruction = "You are 'CodeNexus', an AI Repo-Architect. Use tools to list files."

    def chat():
        print("--- CodeNexus Autonomous Mode Active ---", flush=True)
        
        # 1. Define tools (Make sure names match your functions exactly)
        tools = [{
        "function_declarations": [
            {
                "name": "list_code_files",
                "description": "Lists files in the repo.",
                "parameters": {"type": "OBJECT", "properties": {"path": {"type": "string"}}}
            },
            {
                "name": "read_multiple_files",
                "description": "Reads multiple files at once for cross-file logic analysis.",
                "parameters": {
                    "type": "OBJECT", 
                    "properties": {
                        "file_paths": {"type": "ARRAY", "items": {"type": "string"}}
                    }
                }
            },
            {
                    "name": "write_doc_file",
                    "description": "Writes a documentation file (.md) to the project.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "filename": {"type": "string", "description": "Name of the .md file"},
                            "content": {"type": "string", "description": "The markdown content to write"}
                        },
                        "required": ["filename", "content"]
                    }
            },
            {
                    "name": "index_everything",
                    "description": "Saves all project code into long-term vector memory for fast retrieval.",
                    "parameters": {"type": "OBJECT", "properties": {}}
                },
                {
                    "name": "ask_memory",
                    "description": "Searches long-term memory for logic without reading files. Use for general questions about the codebase.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "question": {"type": "string", "description": "The concept or logic to find in memory"}
                        },
                        "required": ["question"]
                    }
                },
                {
                    "name": "apply_code_fix",
                    "description": "Overwrites a code file with improved content. Use this to fix technical debt or bugs.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "file_path": {"type": "string", "description": "Path to the .py file"},
                            "new_content": {"type": "string", "description": "The complete new code for the file"}
                        },
                        "required": ["file_path", "new_content"]
                    }
                },
                {
                    "name": "web_search",
                    "description": "Searches the live internet for coding documentation, 2026 library updates, and error fixes.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "query": {"type": "string", "description": "The search query to look up on the web"}
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "capture_screen",
                    "description": "Takes a screenshot of the user's screen to analyze UI, terminal errors, or code.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "label": {"type": "string", "description": "What the AI is looking for"}
                        }
                    }
                },
                {
                    "name": "create_new_file",
                    "description": "Creates a new code file (like .py, .js, .css) with the specified content.",
                    "parameters": {
                        "type": "OBJECT",
                        "properties": {
                            "file_path": {"type": "string", "description": "The path and name of the new file"},
                            "content": {"type": "string", "description": "The full code content to write into the file"}
                        },
                        "required": ["file_path", "content"]
                    }
                },
                
         
            
        ]
    },
    # Built-in Google Search tool must be OUTSIDE the function_declarations dictionary
            #{"google_search": {}}
    ]

        # Create a dictionary to easily call functions by their name
        
        available_functions = {
            "list_code_files": list_code_files,
            "read_multiple_files": read_multiple_files,
            "write_doc_file": write_doc_file,
            "index_everything": index_everything,
            "ask_memory": ask_memory,
            "apply_code_fix":apply_code_fix,
            "web_search": web_search,
            "capture_screen": capture_screen,
            "create_new_file": create_new_file
           
        }
        # 1. The Architect: Now a Research-Led Engineer
        architect_instruction = """
        You are the Lead Architect. Your goal is to solve problems with the most modern, stable methods.
        - If a task involves a library, API, or error you aren't 100% sure about in 2026, use 'web_search' immediately.
        - Cross-reference multiple sources if needed.
        - Only propose code once you have verified the syntax.
        
        SYSTEM REFLEX: You are a multi-sensory engineer.

        If a user provides a Screenshot with an error, you must immediately call web_search to find the solution and ask_memory to locate the relevant file in the repo.

        Do not ask for permission to use your senses; provide a unified solution based on all available data (Pixels, Web, and Local Memory).

        If the Reviewer rejects a fix, use web_search to fact-check the Reviewer's claims before proposing a counter-fix.
        """

        # 2. The Reviewer: Now a Fact-Checker
        reviewer_instruction = """
        You are the Senior Reviewer. Your goal is to catch mistakes and verify technical claims.
        - If the Architect proposes a solution using a library, use 'web_search' to verify the documentation is current for 2026.
        - Reject any code that uses deprecated methods or has security flaws.
        - Only respond with 'LGTM' if you have verified the logic is technically sound.
        """
        vision_context = None
        while True:
            user_text = input("\n[USER]: ")
            if user_text.lower() in ["exit", "quit"]:
                break
            # 1. START building the multi-part message
            user_parts = [types.Part.from_text(text=user_text)]

            # 2. VISION HANDLER: If a screenshot exists, attach it
            # Check for NEW screenshot
            if os.path.exists("last_vision_capture.png"):
                with open("last_vision_capture.png", "rb") as f:
                    vision_context = f.read() # Store in persistent variable
                os.remove("last_vision_capture.png")
                print("[SYSTEM]: New visual evidence acquired.")

            # If we have a stored image, always attach it to provide "short-term visual memory"
            if vision_context:
                user_parts.append(types.Part.from_bytes(
                    data=vision_context,
                    mime_type="image/png"
                ))

            # 3. Create the messages list using our combined parts
            messages = [
                types.Content(
                    role="user", 
                    parts=user_parts
                )
            ]
            

            # Start the loop
            for _ in range(5): 
                response = client.models.generate_content(
                    model=model_id,
                    config=types.GenerateContentConfig(
                        system_instruction=architect_instruction,
                        tools=tools
                    ),
                    contents=messages
                )

                if not response.candidates or not response.candidates[0].content:
                    print("\n[SYSTEM]: Gemini returned an empty response. Retrying...")
                    continue
                # --- NEW: Check for Search Grounding ---
                if response.candidates[0].grounding_metadata:
                    print(f"\n[RESEARCH]: Found info via Google Search. Sources checked.")

                messages.append(response.candidates[0].content)
                found_call = False

                if response.candidates[0].content.parts:
                    for part in response.candidates[0].content.parts:
                        if part.function_call:
                            found_call = True
                            call = part.function_call
                            
                            # --- 1. SPECIAL HANDLING: MULTI-AGENT HANDSHAKE ---
                            if call.name == "apply_code_fix":
                                print(f"\n[ARCHITECT]: Proposing fix for {call.args['file_path']}. Sending to Reviewer...")
                                
                               # Setup the context for the Reviewer
                                review_context = f"The Architect wants to change {call.args['file_path']} to this:\n\n{call.args['new_content']}"
                                review_messages = [types.Content(role="user", parts=[types.Part.from_text(text=review_context)])]
                                
                                # --- START OF THE REVIEWER LOOP (PHASE 3 FIX) ---
                                for _ in range(3):  # Give the Reviewer up to 3 turns to research/think
                                    review_response = client.models.generate_content(
                                        model=model_id,
                                        config=types.GenerateContentConfig(system_instruction=reviewer_instruction, tools=tools),
                                        contents=review_messages
                                    )
                                    
                                    review_call_found = False
                                    if review_response.candidates[0].content.parts:
                                        for p in review_response.candidates[0].content.parts:
                                            if p.function_call:
                                                review_call_found = True
                                                r_call = p.function_call
                                                print(f"[REVIEWER ACTION]: Using {r_call.name} to verify fix...")
                                                
                                                # Execute the tool the Reviewer requested
                                                r_result = available_functions[r_call.name](**r_call.args)
                                                
                                                # Feed the tool result back to the Reviewer
                                                review_messages.append(review_response.candidates[0].content)
                                                review_messages.append(types.Content(
                                                    role="tool", 
                                                    parts=[types.Part.from_function_response(
                                                        name=r_call.name, 
                                                        response={"result": r_result}
                                                    )]
                                                ))
                                    
                                    if not review_call_found:
                                        break # Reviewer finished thinking and provided a text verdict
                                
                                # Capture the final text verdict
                                review_text = review_response.text if review_response.text else "The Reviewer provided no text verdict."
                                print(f"\n[REVIEWER AUDIT]:\n{review_text}")
                                print("-" * 50)

                                review_text = review_response.text or ""
                                if "LGTM" in review_text.upper():
                                    # ONLY PROCEED TO PREVIEW IF REVIEWER SAYS LGTM
                                    print(f"\n--- 🛡️ SECURITY PREVIEW: {call.args['file_path']} ---")
                                    content_lines = call.args['new_content'].splitlines()
                                    if len(content_lines) > 20:
                                        print("\n".join(content_lines[:10]))
                                        print(f"\n... [AI is proposing {len(content_lines)} lines] ...\n")
                                        print("\n".join(content_lines[-10:]))
                                    else:
                                        print(call.args['new_content'])
                                    
                                    confirm = input(f"\nReviewer approved this. Final user permission to write? (y/n): ")
                                    if confirm.lower() == 'y':
                                        result = available_functions[call.name](**call.args)
                                        print("✅ Fix Applied.")
                                    else:
                                        result = "User REJECTED the code change after Reviewer approval."
                                        print("❌ Fix Cancelled.")
                                else:
                                    # Reviewer found a bug!
                                    result = f"Reviewer REJECTED this fix for the following reasons: {review_response.text}"
                                    print("❌ Reviewer REJECTED the fix. Architect notified.")

                            # --- 2. NORMAL TOOL HANDLING ---
                            else:
                                print(f"\n[AI ACTION]: Wants to use {call.name}")
                                if call.name in available_functions:
                                    result = available_functions[call.name](**call.args)
                                else:
                                    result = f"Error: Tool {call.name} not found."

                            # 3. Send the result back to Gemini (Architect)
                            messages.append(types.Content(
                                role="tool",
                                parts=[types.Part.from_function_response(
                                    name=call.name,
                                    response={"result": result}
                                )]
                            ))

                    if not found_call:
                        if response.text:
                            print(f"\n[CODENEXUS]: {response.text}")
                        break
    if __name__ == "__main__":
        chat()
except Exception as e:
    print(f"An error occurred during execution: {e}")