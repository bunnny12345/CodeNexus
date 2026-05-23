import os
from dotenv import load_dotenv
from memory_engine import index_project_file

# Load environment configs
load_dotenv()

def list_code_files(path="."):
    files = []
    exclude_dirs = {'venv', '.git', '__pycache__', 'node_modules', 'nexus_memory'}
    for root, dirs, filenames in os.walk(path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for filename in filenames:
            if filename.endswith(('.py', '.js', '.ts', '.html', '.css', '.sql', 
                '.mp3', '.h5', '.ipynb', '.md', '.txt')) or filename == ".env":
                files.append(os.path.join(root, filename))
    return files

def run_indexing_sweep():
    print("🛰️ CodeNexus Database Ingestion Initialized...")
    target_files = list_code_files()
    print(f"📋 Found {len(target_files)} project files to process.")
    
    for idx, file_path in enumerate(target_files, 1):
        print(f"📦 Processing [{idx}/{len(target_files)}]: {file_path}...")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            status = index_project_file(file_path, content)
            print(f"   {status}")
        except Exception as e:
            print(f"   ❌ Failed to process {file_path}: {str(e)}")
            
    print("\n✅ Database Knowledge Activation Complete!")

if __name__ == "__main__":
    run_indexing_sweep()