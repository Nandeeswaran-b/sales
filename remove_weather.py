import re

for filepath in ['frontend/index.html', 'backend/templates/index.html']:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove the tab button
    content = re.sub(r'\s*<button class="tab-btn" onclick="switchTab\(\'weather\'\)" id="tab-weather">🌦️ Weather Prediction</button>', '', content)
    
    # 2. Remove the weather-view block
    content = re.sub(r'\s*<!-- Weather Prediction Tab -->.*?<!-- SQL Sandbox Tab -->', '\n\n    <!-- SQL Sandbox Tab -->', content, flags=re.DOTALL)
    
    # 3. Remove from switchTab
    content = re.sub(r'} else if \(tabId === \'weather\'\) \{\s*loadWeatherForecast\(\);\s*', '', content)
    
    # 4. Remove loadWeatherForecast function
    content = re.sub(r'\s*// WEATHER-BASED SALES PREDICTIONS.*?(?=\s*// APP TRIGGER)', '\n\n    ', content, flags=re.DOTALL)
    
    # 5. Remove from hashes
    content = content.replace(" || hash === 'weather'", "")
    content = content.replace(" || initialHash === 'weather'", "")
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print('Weather feature removed successfully.')
