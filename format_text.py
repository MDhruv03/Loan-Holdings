import glob
for filepath in glob.glob('templates/**/*.html', recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = f.read()
    
    data = data.replace('tracking-widest', 'tracking-wider')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f'Softened tracking in {filepath}')
