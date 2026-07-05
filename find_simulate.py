import subprocess, sys

result = subprocess.run(['git', 'show', 'bfb5739:frontend/index.html'], capture_output=True)
old = result.stdout.decode('utf-8')

# Find all "Simulate" mentions
lines = old.split('\n')
found = []
for i, line in enumerate(lines):
    if 'simulate' in line.lower() or 'Simulate' in line:
        found.append(f'{i+1}: {line[:120]}')

with open('simulate_lines.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(found))

print(f'Found {len(found)} references. Saved to simulate_lines.txt')
