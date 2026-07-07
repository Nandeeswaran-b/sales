import re

def check_html_nesting(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We want to check nesting of main tags: <div>, </div>
    # Let's count them or parse them.
    # To keep it simple, we can trace open/close tags and find where it goes wrong.
    # Let's tokenize and track the stack of tags.
    # A simple regex tokenizer for tags:
    tag_regex = re.compile(r'<(/?)([a-zA-Z0-9:-]+)([^>]*)>')
    
    stack = []
    lines = content.split('\n')
    
    print(f"Analyzing {filepath}...")
    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1
        for match in tag_regex.finditer(line):
            is_close = match.group(1) == '/'
            tag_name = match.group(2).lower()
            attrs = match.group(3)
            
            # Skip self-closing tags or tags that don't need closing in HTML
            # but usually we should track div, section, main, header, form, canvas etc.
            if tag_name in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                continue
            if attrs.endswith('/'):
                continue
                
            if tag_name == 'div':
                if is_close:
                    if not stack:
                        print(f"Error: Excess closing </div> at line {line_num}: {line.strip()[:100]}")
                    else:
                        popped = stack.pop()
                        # print(f"Closed div from line {popped[0]}")
                else:
                    # Find id or class
                    id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
                    class_match = re.search(r'class=["\']([^"\']+)["\']', attrs)
                    info = ""
                    if id_match:
                        info += f" id={id_match.group(1)}"
                    if class_match:
                        info += f" class={class_match.group(1)}"
                    stack.append((line_num, info))
                    
    print(f"Nesting check complete. Stack depth at end: {len(stack)}")
    if stack:
        print("Unclosed divs:")
        for line_num, info in stack:
            print(f"  Line {line_num}:{info}")

check_html_nesting('temp_good_frontend_utf8.html')
