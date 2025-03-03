#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Even if you have all the packages herein imported
you might have to install openpyxl and xlrd in order for this code to work
"""


import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from tqdm import tqdm

# Load the Excel file
input_file = "~/MedicNetworks.xls" #Configure the Path according to the place where you have the Patnetscope result list 
data = pd.read_excel(input_file)

# Handle NaN values and split columns
data['Applicants'] = data['Applicants'].fillna('').str.split(';')
data['Inventors'] = data['Inventors'].fillna('').str.split(';')

# Define a function to clean applicant names
def clean_applicant_name(name):
    name = name.strip()
    if name.lower().endswith(', inc') or name.lower().endswith(', inc.'):
        name = name[:name.lower().rfind(', inc')].strip()
    return name

# Define a function to check for similar values
def has_similar_value(applicant, inventors):
    applicant = applicant.lower().strip()
    for inventor in inventors:
        inventor = inventor.lower().strip()
        if any(applicant[i:i+5] in inventor for i in range(len(applicant) - 4)):
            return True
    return False

# Initialize the filtered data
filtered_rows = []

# Step 1: Filter rows and remove applicants similar to inventors
for _, row in tqdm(data.iterrows(), total=len(data), desc="Filtering rows"):
    applicants = row['Applicants']
    inventors = row['Inventors']

    # Skip rows where any applicant matches any inventor exactly
    if any(applicant.strip().lower() == inventor.strip().lower() for applicant in applicants for inventor in inventors):
        continue

    # Filter out applicants that are similar to inventors
    filtered_applicants = [clean_applicant_name(applicant) for applicant in applicants if not has_similar_value(applicant, inventors)]

    # Select the first applicant if multiple remain
    selected_applicant = filtered_applicants[0] if filtered_applicants else None
    if selected_applicant:
        filtered_rows.append({"Applicant": selected_applicant, "Inventors": '; '.join(inventors)})

# Create the filtered DataFrame
filtered_data = pd.DataFrame(filtered_rows)

# Step 2: Compact the table by grouping applicants
compacted_data = (
    filtered_data.groupby(filtered_data['Applicant'].str.lower())
    .agg({"Inventors": lambda x: '; '.join(set('; '.join(x).split('; ')))}).reset_index()
)
compacted_data.columns = ['Applicant', 'Inventors']

# Save the compacted table
output_file = "Filtered.xlsx"
compacted_data.to_excel(output_file, index=False, engine="openpyxl")

# Step 3: Build the network graph
G = nx.Graph()

# Add edges based on shared inventors
for i, row1 in tqdm(compacted_data.iterrows(), total=len(compacted_data), desc="Building graph"):
    for j, row2 in compacted_data.iterrows():
        if i >= j:
            continue
        shared_inventors = set(row1['Inventors'].split('; ')) & set(row2['Inventors'].split('; '))
        weight = len(shared_inventors)
        if weight > 0:
            G.add_edge(row1['Applicant'], row2['Applicant'], weight=weight)

# Step 4: Select the top 10 most connected applicants
degrees = sorted(G.degree, key=lambda x: x[1], reverse=True)[:20]
top_nodes = [node for node, _ in degrees]
H = G.subgraph(top_nodes)

# Step 5: Draw the graph
plt.figure(figsize=(12, 12))
pos = nx.circular_layout(H)
nx.draw(
    H, pos, with_labels=True, node_size=3000, font_size=10, 
    font_weight='bold', edge_color='gray', node_color='skyblue'
)
labels = nx.get_edge_attributes(H, 'weight')
nx.draw_networkx_edge_labels(H, pos, edge_labels=labels, font_size=8)
plt.title("Top 10 Most Connected Applicants", fontsize=16)
plt.show()
