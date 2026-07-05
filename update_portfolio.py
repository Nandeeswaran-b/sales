import urllib.request, json, base64

# GitHub Personal Access Token - needed to push to portfolio repo
# Since we can't do it programmatically without a token, 
# let's generate the corrected data.ts content and output it

with open('portfolio_data.ts', 'r', encoding='utf-8') as f:
    content = f.read()

with open('portfolio_data_updated.ts', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated portfolio_data.ts ready.")
print("\nTo apply to portfolio, copy the content of portfolio_data_updated.ts")
print("to frontend/src/lib/data.ts in the nandeeswaran-portfolio repo.")
