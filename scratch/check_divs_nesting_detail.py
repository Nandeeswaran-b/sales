import re

def check_html_nesting_detail(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tag_regex = re.compile(r'<(/?)(div|header|section|main|form|canvas)\b([^>]*)>', re.IGNORECASE)
    
    stack = []
    lines = content.split('\n')
    
    log = []
    
    for line_idx, line in enumerate(lines):
        line_num = line_idx + 1
        for match in tag_regex.finditer(line):
            is_close = match.group(1) == '/'
            tag_name = match.group(2).lower()
            attrs = match.group(3)
            
            if attrs.endswith('/'):
                continue
                
            if is_close:
                if not stack:
                    log.append(f"Excess closing </{tag_name}> at line {line_num}: {line.strip()[:100]}")
                else:
                    popped_line, popped_tag, popped_info = stack.pop()
                    if popped_tag != tag_name:
                        log.append(f"Mismatch at line {line_num}: </{tag_name}> closes <{popped_tag}{popped_info}> from line {popped_line}")
            else:
                id_match = re.search(r'id=["\']([^"\']+)["\']', attrs)
                class_match = re.search(r'class=["\']([^"\']+)["\']', attrs)
                info = ""
                if id_match:
                    info += f" id={id_match.group(1)}"
                if class_match:
                    info += f" class={class_match.group(1)}"
                stack.append((line_num, tag_name, info))
                
    if stack:
        log.append(f"Unclosed tags at end of file:")
        for line_num, tag_name, info in stack:
            log.append(f"  Line {line_num}: <{tag_name}{info}>")
            
    with open('nesting_report.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(log))
    print(f"Report written to nesting_report.txt, found {len(log)} issues")

check_html_nesting_detail('frontend/index.html')
