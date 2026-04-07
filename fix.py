import re
import textwrap

with open('app/streamlit_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

def fix_fstring(match):
    inside = match.group(1)
    dedented = textwrap.dedent(inside)
    return f'f"""{dedented}"""'

content = re.sub(r'f\"\"\"(.*?)\"\"\"', fix_fstring, content, flags=re.DOTALL)

def fix_string(match):
    inside = match.group(1)
    dedented = textwrap.dedent(inside)
    return f'"""{dedented}"""'

content = re.sub(r'(?<!f)\"\"\"(.*?)\"\"\"', fix_string, content, flags=re.DOTALL)

with open('app/streamlit_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
