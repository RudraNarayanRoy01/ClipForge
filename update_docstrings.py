import os

files = [
    'execution_engine_descriptor_factory.py',
    'execution_engine_factory.py',
    'execution_engine_metadata_factory.py',
    'execution_engine_snapshot_factory.py',
    'execution_engine_statistics_builder.py',
    'runtime_execution_engine_factory.py'
]

target_docstring = '''    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Providers
    Monitoring
    Telemetry
    Optimization
    Routing
    Planning
    Hardware
    Dependency Injection
    """'''

for file in files:
    filepath = os.path.join('backend/src/runtime/execution', file)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    start_idx = content.find('    """\n    ONLY performs structural construction.')
    if start_idx == -1:
        print(f"Could not find start in {file}")
        continue
        
    end_idx = content.find('    """', start_idx + 10)
    if end_idx == -1:
        print(f"Could not find end in {file}")
        continue
        
    end_idx += 7
    
    new_content = content[:start_idx] + target_docstring + content[end_idx:]
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f'Updated {file}')
