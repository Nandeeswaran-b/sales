import re

with open('frontend/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract script
match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
script = match.group(1)

# Find all variables and functions declared
declarations = re.findall(r'\b(var|let|const|function)\s+([a-zA-Z0-9_]+)', script)
declared_names = set(name for type_, name in declarations)

# Add standard web globals and known libraries
globals_set = {
    'window', 'document', 'console', 'fetch', 'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval',
    'JSON', 'Math', 'Date', 'parseInt', 'parseFloat', 'Intl', 'AbortController', 'Promise', 'performance',
    'Chart', 'location', 'activeTab', 'allSalesData', 'anomalySet', 'forecastDegree', 'rfmCustomerList',
    'API_BASE', 'currencyFormatter', 'charts', 'anomalyRes', 'recsRes', 'statsRes', 'rfmRes', 'monthlyRes',
    'categoryRes', 'customersRes', 'salesRes', 'forecastRes', 'correlationRes', 'distributionRes', 'growthRes'
}

all_allowed = declared_names.union(globals_set)

# Find all word tokens in the script
tokens = set(re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', script))

# Find potentially undeclared words
keywords = {
    'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue', 'return', 'true', 'false',
    'null', 'undefined', 'new', 'typeof', 'instanceof', 'try', 'catch', 'finally', 'throw', 'function',
    'var', 'let', 'const', 'async', 'await', 'import', 'export', 'default', 'class', 'extends', 'super',
    'this', 'in', 'of', 'debugger', 'void', 'delete', 'with', 'yield', 'let', 'static', 'get', 'set'
}

potential_issues = []
for t in tokens:
    if t not in all_allowed and t not in keywords:
        usages = re.findall(r'(?<!\.)\b' + t + r'\b(?!:)', script)
        if usages:
            potential_issues.append(t)

with open('undeclared_report.txt', 'w', encoding='utf-8') as f:
    f.write("Potential undeclared variables/functions used:\n")
    for p in sorted(potential_issues):
        for line_idx, line in enumerate(script.split('\n')):
            if re.search(r'(?<!\.)\b' + p + r'\b(?!:)', line):
                safe_line = line.strip().encode('ascii', errors='replace').decode('ascii')
                f.write(f"  Line {line_idx+1}: {p} -> {safe_line[:100]}\n")

print("Done. Report written to undeclared_report.txt")
