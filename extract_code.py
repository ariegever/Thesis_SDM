import json
import sys

def extract_code(notebook_path):
    try:
        with open(notebook_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
        
        for i, cell in enumerate(nb.get('cells', [])):
            if cell.get('cell_type') == 'code':
                source = ''.join(cell.get('source', []))
                print(f"--- Cell {i} ---")
                print(source)
                print("\n")
    except Exception as e:
        print(f"Error reading notebook: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_code.py <notebook_path>")
    else:
        extract_code(sys.argv[1])
