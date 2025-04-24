import json
import os

def load_json(filename):
    if not os.path.exists(filename):
        # אם הקובץ לא קיים, יוצרים חדש בהתאם לסיומת
        if filename.endswith('.json'):
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({}, f, ensure_ascii=False, indent=2)
        return {} if 'answers' in filename or 'game_state' in filename else []

    with open(filename, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
