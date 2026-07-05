import re, sys

for filepath in ['frontend/index.html', 'backend/templates/index.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)

    # 1. Remove loose churn HTML block
    content = re.sub(
        r'\s*<!-- Filters Panel -->.*?<!-- Details Table -->.*?</div>\s*</div>\s*</div>\s*\n\s*\n\s*\n',
        '\n\n',
        content,
        flags=re.DOTALL
    )

    # 2. Remove loadChurnData JS function
    content = re.sub(
        r'\s*async function loadChurnData\(\).*?(?=\s*function |\s*// ={3,}|\s*window\.)',
        '\n\n    ',
        content,
        flags=re.DOTALL
    )

    # 3. Remove takeRetentionAction
    content = re.sub(
        r'\s*window\.takeRetentionAction\s*=.*?(?=\s*async function |\s*// ={3,}|\s*window\.)',
        '\n\n    ',
        content,
        flags=re.DOTALL
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    new_len = len(content)

    with open('cleanup_log.txt', 'a', encoding='utf-8') as log:
        log.write(f'{filepath}: removed {original_len - new_len} chars\n')
        for c in ['churnPieChart', 'loadChurnData', 'Churn Segment Filters', 'takeRetentionAction']:
            log.write(f'  {c}: {"STILL PRESENT" if c in content else "removed"}\n')
        for c in ['dashboard-view', 'sql-view', 'simModal', 'loadSQLConsoleData']:
            log.write(f'  {c}: {"present" if c in content else "MISSING"}\n')
        log.write('\n')

print('Done. Check cleanup_log.txt')
