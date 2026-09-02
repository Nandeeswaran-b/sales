import subprocess

# Check all commits for sim-modal
commits = ['fd6fca9','dbd6919','f637303','e104b68','b060ba9','c6a35da','71bad7c','bfb5739','2e04bf5','a359c67']
for commit in commits:
    result = subprocess.run(['git', 'show', f'{commit}:frontend/index.html'], capture_output=True)
    if result.returncode == 0:
        old = result.stdout.decode('utf-8')
        has = 'sim-modal' in old
        has2 = 'sim-overlay' in old
        has3 = 'simModal' in old
        print(f'{commit}: sim-modal={has}, sim-overlay={has2}, simModal={has3}')
