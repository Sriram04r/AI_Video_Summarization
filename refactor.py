import os

frontend_src = r"c:\Users\srira\OneDrive\Documents\Desktop\AI_VIDEO_SUMMARIZATION\frontend\src"

def safe_replace(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    changed = False
    for i, line in enumerate(lines):
        if 'http://127.0.0.1:8000' in line:
            # If it's using single quotes
            if "'http://127.0.0.1:8000" in line:
                line = line.replace("'http://127.0.0.1:8000", "`${import.meta.env.VITE_API_BASE_URL}")
                line = line.replace("', {", "`, {")
                line = line.replace("')", "`)")
            # If it's using backticks
            elif "`http://127.0.0.1:8000" in line:
                line = line.replace("`http://127.0.0.1:8000", "`${import.meta.env.VITE_API_BASE_URL}")
            
            lines[i] = line
            changed = True
            
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

for root, _, files in os.walk(frontend_src):
    for file in files:
        if file.endswith('.jsx'):
            safe_replace(os.path.join(root, file))

print("URL refactoring complete!")
