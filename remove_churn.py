import re

for filepath in ['frontend/index.html', 'backend/templates/index.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the tab button
    content = re.sub(r'\s*<button class="tab-btn" onclick="switchTab\(\'churn\'\)" id="tab-churn">👥 Churn Prediction</button>', '', content)
    
    # 2. Remove the churn-view block
    content = re.sub(r'\s*<!-- Churn Prediction Tab -->.*?<!-- SQL Sandbox Tab -->', '\n\n    <!-- SQL Sandbox Tab -->', content, flags=re.DOTALL)
    
    # 3. Remove from switchTab
    content = re.sub(r'} else if \(tabId === \'churn\'\) \{\s*loadChurnData\(\);\s*', '', content)
    
    # 4. Remove loadChurnData function
    content = re.sub(r'\s*// CHURN PREDICTION ENGINE.*?(?=\s*// SQL SANDBOX)', '\n\n    ', content, flags=re.DOTALL)
    
    # 5. Remove from hashes
    content = content.replace(" || hash === 'churn'", "")
    content = content.replace(" || initialHash === 'churn'", "")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Churn feature removed successfully.')
