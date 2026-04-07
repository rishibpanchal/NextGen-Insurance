import re

with open('app/streamlit_app.py', 'r', encoding='utf-8') as f:
    text = f.read()

def strip_all_spaces(match):
    lines = match.group(1).split('\n')
    stripped = [line.lstrip() for line in lines]
    return f'f"""{"".join(stripped)}"""'

text = re.sub(r'f\"\"\"(.*?)\"\"\"', strip_all_spaces, text, flags=re.DOTALL)

def strip_all_spaces_str(match):
    lines = match.group(1).split('\n')
    stripped = [line.lstrip() for line in lines]
    return f'"""{"".join(stripped)}"""'

text = re.sub(r'(?<!f)\"\"\"(.*?)\"\"\"', strip_all_spaces_str, text, flags=re.DOTALL)

with open('app/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(text)
