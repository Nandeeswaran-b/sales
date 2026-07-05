with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find all tags with class containing 'tab-content' or id containing 'view'
tags = re.findall(r'<[a-zA-Z0-9:-]+\s+[^>]*class=["\'][^"\']*tab-content[^"\']*["\'][^>]*>', content)
print("Tags with tab-content class:")
for t in tags:
    print(" ", t)

ids = re.findall(r'<[a-zA-Z0-9:-]+\s+[^>]*id=["\'][^"\']*view[^"\']*["\'][^>]*>', content)
print("Tags with id containing view:")
for i in ids:
    print(" ", i)
