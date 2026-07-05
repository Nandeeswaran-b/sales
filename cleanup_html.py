def remove_div_block(content, div_id):
    marker = f'id="{div_id}"'
    pos = content.find(marker)
    if pos == -1:
        print(f"{div_id} NOT FOUND")
        return content
    
    # Walk back to find the opening <div
    start = content.rfind('<div', 0, pos)
    
    # Walk forward counting depth to find closing </div>
    depth = 0
    i = start
    while i < len(content):
        if content[i:i+4] == '<div':
            depth += 1
        elif content[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                break
        i += 1
    
    # Also remove surrounding comment if present
    comment_start = content.rfind('<!--', 0, start)
    if comment_start != -1:
        text_between = content[comment_start:start].strip()
        comment_end = content.find('-->', comment_start)
        if comment_end != -1 and comment_end < start + 5:
            start = comment_start
    
    removed = content[start:end]
    print(f"Removing {div_id} block ({len(removed)} chars)")
    return content[:start] + content[end:]

for filepath in ['frontend/index.html', 'backend/templates/index.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = remove_div_block(content, 'churn-view')
    content = remove_div_block(content, 'weather-view')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Done: {filepath}")
