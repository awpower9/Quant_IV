import os, re

dashboard_dir = r"c:\QUANTIV_FINAL\dashboard"

for root, dirs, files in os.walk(dashboard_dir):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8") as file:
                content = file.read()
            
            # Replace '($)' with '(₹)'
            content = content.replace("($)", "(₹)")
            
            # Replace '$' followed by { (e.g. ${price})
            content = re.sub(r'\$(?=\{)', '₹', content)
            
            # Replace '$' followed by % (e.g. $%{y})
            content = re.sub(r'\$(?=\%)', '₹', content)
            
            # Replace '$' followed by a digit (e.g. $1.00)
            content = re.sub(r'\$(?=\d)', '₹', content)
            
            with open(p, "w", encoding="utf-8") as file:
                file.write(content)

print("Currency symbols updated to INR.")
