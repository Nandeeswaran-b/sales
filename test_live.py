import subprocess, re

# Get the live page content
with open(r'C:\Users\Lenovo\.gemini\antigravity\brain\9e0257c7-d071-491e-95c6-26f1fab06ab7\.system_generated\steps\1092\content.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the script
match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
if not match:
    print("No script tag found!")
    exit()

script = match.group(1)
print(f"Script length: {len(script)} chars")

js_wrapper = '''
global.window = new Proxy({
    location: { hash: '', hostname: 'localhost' },
    addEventListener: () => {},
    print: () => {}
}, {
    set(obj, prop, value) { global[prop] = value; obj[prop] = value; return true; }
});
global.document = {
    addEventListener: () => {},
    querySelectorAll: (sel) => ({ forEach: () => {} }),
    getElementById: (id) => ({
        getContext: () => ({ clearRect: ()=>{}, fillRect: ()=>{} }),
        classList: { add: () => {}, remove: () => {}, contains: () => false },
        addEventListener: () => {},
        textContent: '',
        innerHTML: '',
        value: '',
        style: {},
        submit: undefined
    }),
    body: { appendChild: () => {} }
};
global.fetch = async () => ({ ok: true, json: async () => ({}) });
global.Chart = class {
    static defaults = { font: {}, color: '', borderColor: '', scale: { grid: {} }, plugins: { tooltip: {} } };
    constructor() {}
};
global.Intl = { NumberFormat: class { format(n) { return n; } } };
'''

full_js = js_wrapper + script

with open('live_test.js', 'w', encoding='utf-8') as f:
    f.write(full_js)

result = subprocess.run(['node', 'live_test.js'], capture_output=True, text=True, timeout=10)
with open('node_errors.txt', 'w', encoding='utf-8') as f:
    f.write('STDOUT:\n' + result.stdout + '\n\nSTDERR:\n' + result.stderr)

print('Done. Check node_errors.txt')
print('Return code:', result.returncode)
