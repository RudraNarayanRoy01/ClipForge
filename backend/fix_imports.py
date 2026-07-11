import os
import re

src_dir = r"d:\My Data\Precious Data\Vibe Code\AI Clipping Platform\backend\src"

count = 0
for root, dirs, files in os.walk(src_dir):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            rel_path = os.path.relpath(filepath, src_dir)
            parts = rel_path.replace('\\', '/').split('/')
            
            if parts[-1] == '__init__.py':
                package_parts = ["src"] + parts[:-1]
            else:
                package_parts = ["src"] + parts[:-1]
            
            def replace_import(match):
                spaces = match.group(1)
                dots = match.group(2)
                module = match.group(3)
                
                num_dots = len(dots)
                
                if num_dots > len(package_parts):
                    return match.group(0)
                    
                target_package = package_parts[:len(package_parts) - num_dots + 1]
                
                prefix = ".".join(target_package)
                if module:
                    new_module = f"{prefix}.{module}"
                else:
                    new_module = prefix
                    
                return f"{spaces}from {new_module} import"

            new_content = re.sub(r'^([ \t]*)from\s+(\.+)([\w\.]*)\s+import', replace_import, content, flags=re.MULTILINE)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed {rel_path}")
                count += 1

print(f"Total files fixed: {count}")
