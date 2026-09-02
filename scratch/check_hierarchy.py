with open('frontend/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
for line_idx, line in enumerate(lines):
    line_num = line_idx + 1
    # Find all div start and close tags
    # A simple way is to find '<div' and '</div>'
    # We want to trace nesting of divs with ids
    import re
    div_starts = re.findall(r'<div\b[^>]*>', line)
    for ds in div_starts:
        id_match = re.search(r'id=["\']([^"\']+)["\']', ds)
        class_match = re.search(r'class=["\']([^"\']+)["\']', ds)
        name = "div"
        if id_match:
            name += f" id={id_match.group(1)}"
        if class_match:
            name += f" class={class_match.group(1)}"
        stack.append((line_num, name))
    
    div_closes = re.findall(r'</div>', line)
    for dc in div_closes:
        if stack:
            popped = stack.pop()
            # If the popped div has an id like dashboard-view, analytics-view, or sql-view, print it
            if 'view' in popped[1] or 'container' in popped[1]:
                print(f"Closed {popped[1]} (opened at line {popped[0]}) on line {line_num}")
        else:
            print(f"Extra closing div on line {line_num}")

print("Remaining stack at end of file:")
for item in stack:
    print(f"  Opened at line {item[0]}: {item[1]}")
