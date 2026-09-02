import subprocess

result = subprocess.run(['git', 'show', 'fd6fca9:frontend/index.html'], capture_output=True)
old = result.stdout.decode('utf-8')

# Find simModal div
start = old.find('id="simModal"')
if start == -1:
    print("simModal NOT FOUND")
else:
    start = old.rfind('<div', 0, start)
    depth = 0
    i = start
    while i < len(old):
        if old[i:i+4] == '<div':
            depth += 1
        elif old[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                end = i + 6
                break
        i += 1
    sim_modal = old[start:end]
    print(f'simModal found: {len(sim_modal)} chars')
    with open('sim_modal.txt', 'w', encoding='utf-8') as f:
        f.write(sim_modal)
    print('Saved to sim_modal.txt')
    print('First 200 chars:', sim_modal[:200])
