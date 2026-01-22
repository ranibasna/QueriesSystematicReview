import os

# Define file paths
base_path = 'studies/Godos_2024/embase_manual_queries'
files = [
    f'{base_path}/embase_query41.csv',
    f'{base_path}/embase_query42.csv',
    f'{base_path}/embase_query43.csv'
]

# Read each file as plain text and count lines
file_contents = []
line_counts = []
for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
        file_contents.append(content)
        lines = content.count('\n')
        line_counts.append(lines)
        print(f'{os.path.basename(file)}: {lines} lines')

# Merge all file contents
# Add a newline between files if the previous file doesn't end with a blank line
merged_content = ''
for i, content in enumerate(file_contents):
    if i > 0 and not merged_content.endswith('\n\n'):
        # Add blank line between records if not already present
        if merged_content.endswith('\n'):
            merged_content += '\n'
        else:
            merged_content += '\n\n'
    merged_content += content

# Count total lines
total_lines = merged_content.count('\n')
expected_lines = sum(line_counts)

print(f'\nTotal lines after merge: {total_lines}')
print(f'Expected lines (sum of individual files): {expected_lines}')
print(f'Match: {total_lines == expected_lines}')

# Save merged file
output_file = f'{base_path}/embase_query4_merged.csv'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(merged_content)
print(f'\nMerged file saved to: {output_file}')
