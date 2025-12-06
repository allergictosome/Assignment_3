import pandas as pd
import json
from collections import defaultdict

# Load the CSV
df = pd.read_csv('data_scopus.csv')

# Filter rows with Year and Authors with affiliations
df = df.dropna(subset=['Year', 'Authors with affiliations'])

# Collect unique authors and co-authorships
authors = {}  # id -> {id, name, affiliation, country}
co_links = defaultdict(int)  # (author_id1, author_id2) -> count

author_id = 0
name_to_id = {}
country_counts = defaultdict(int)

for _, row in df.iterrows():
    aff_str = row['Authors with affiliations']
    valid_authors = []
    for entry in aff_str.split(';'):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(',', 1)
        if len(parts) < 2:
            continue
        name = parts[0].strip()
        affiliation = parts[1].strip()
        if not name or not affiliation:
            continue
        # Parse country: last part after comma
        aff_parts = [p.strip() for p in affiliation.split(',')]
        country = aff_parts[-1] if aff_parts else 'Unknown'
        
        if name not in name_to_id:
            aid = str(author_id)
            name_to_id[name] = aid
            authors[aid] = {'id': aid, 'name': name, 'affiliation': affiliation, 'country': country}
            country_counts[country] += 1
            author_id += 1
        valid_authors.append(name_to_id[name])
    
    if len(valid_authors) < 2:
        continue
    
    # Add undirected weighted links
    for i in range(len(valid_authors)):
        for j in range(i+1, len(valid_authors)):
            key = tuple(sorted([valid_authors[i], valid_authors[j]]))
            co_links[key] += 1

# Build nodes and links
nodes = list(authors.values())
links = [{'source': k[0], 'target': k[1], 'value': v} for k, v in co_links.items()]

# Compute degrees
for node in nodes:
    node['degree'] = sum((1 for link in links if link['source'] == node['id'] or link['target'] == node['id']))

# Top 10 countries
top_countries = sorted(country_counts, key=country_counts.get, reverse=True)[:10]

# Output JSON
output = {'nodes': nodes, 'links': links, 'top_countries': top_countries}
with open('network.json', 'w') as f:
    json.dump(output, f, indent=2)

print("Processed data saved to network.json")