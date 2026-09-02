import subprocess, re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract the script
match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
script = match.group(1)

js_wrapper = '''
global.window = new Proxy({
    location: { hash: '#sql', hostname: 'localhost' },
    addEventListener: () => {},
    print: () => {}
}, {
    set(obj, prop, value) { global[prop] = value; obj[prop] = value; return true; }
});
global.document = {
    addEventListener: () => {},
    querySelectorAll: (sel) => {
        return [
            { id: 'tab-dashboard', classList: { add: () => {}, remove: () => {} } },
            { id: 'tab-analytics', classList: { add: () => {}, remove: () => {} } },
            { id: 'tab-sql', classList: { add: () => {}, remove: () => {} } },
            { id: 'dashboard-view', classList: { add: () => {}, remove: () => {} } },
            { id: 'analytics-view', classList: { add: () => {}, remove: () => {} } },
            { id: 'sql-view', classList: { add: () => {}, remove: () => {} } }
        ];
    },
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
global.performance = { now: () => Date.now() };
global.setTimeout = setTimeout;
'''

# Append execution of switchTab and loadSQLConsoleData at the end
test_calls = '''
console.log("Calling switchTab('sql')...");
switchTab('sql');
console.log("Calling loadSQLConsoleData()...");
loadSQLConsoleData();
console.log("Calling openSimModal()...");
openSimModal();
console.log("Calling closeSimModal()...");
closeSimModal();
console.log("All calls executed successfully!");
'''

full_js = js_wrapper + script + test_calls

with open('test_tabs.js', 'w', encoding='utf-8') as f:
    f.write(full_js)

result = subprocess.run(['node', 'test_tabs.js'], capture_output=True, text=True)
print("STDOUT:")
print(result.stdout)
print("STDERR:")
print(result.stderr)
print("Exit code:", result.returncode)
