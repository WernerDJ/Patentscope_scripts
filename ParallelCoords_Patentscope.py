#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 26 19:08:30 2024

@author: werner
"""

import pandas as pd
import re
from collections import Counter
# Calculating and Plotting
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
import numpy as np
# Load the Excel file
file_path = '/home/werner/Desktop/MedicNetworks.xls'
sheet_name = 'ResultSet'
df = pd.read_excel(file_path, sheet_name=sheet_name)

# Filter out rows where 'Applicants' contains 'Rockwool'
df_filtered = df[~df['Applicants'].str.contains(
    'Rockwool', case=False, na=False)]

# Extract the year from 'Publication Date' and create 'PubYear' column
df_filtered['PubYear'] = pd.to_datetime(
    df_filtered['Publication Date'], format='%d.%m.%Y', errors='coerce').dt.year

# Extract the earliest year from 'Priorities Data' and create 'PriYear' column


def extract_earliest_year(priorities):
    if pd.isna(priorities):
        return None

    # Extract all four-digit years (ensures we only consider valid years like 2000, 2021, etc.)
    years = re.findall(r'\b(19\d{2}|20\d{2})\b', str(priorities))

    # Convert extracted years to integers
    years = [int(year) for year in years]

    # Return the minimum year if any valid years are found
    return min(years) if years else None


# Apply the function to the 'Priorities Data' column
df_filtered['PriYear'] = df_filtered['Priorities Data'].apply(
    extract_earliest_year)

# Fill empty PriYear values with PubYear values
df_filtered['PriYear'].fillna(df_filtered['PubYear'], inplace=True)

# Extract MainIPC from 'I P C' column


def extract_main_ipc(ipc_codes):
    if pd.isna(ipc_codes):
        return None

    # Extract all IPC codes
    codes = re.findall(r'\b[A-Z]\d{2}[A-Z]?', str(ipc_codes))

    if not codes:
        return None

    # Extract first 4 characters of each code
    short_codes = [code[:4] for code in codes]

    # Count occurrences
    counter = Counter(short_codes)
    most_common = counter.most_common(1)

    # Return most common if available, else return the first one
    return most_common[0][0] if most_common else short_codes[0]


# Apply MainIPC extraction
df_filtered['MainIPC'] = df_filtered['I P C'].apply(extract_main_ipc)
'''
# Save the filtered data to a new Excel file
output_file = '/home/werner/Desktop/filtered_results_with_mainipc.xlsx'
df_filtered.to_excel(output_file, index=False)

print(f"Filtered data saved to: {output_file}")
'''
'''
#########################################################
Calculating and Plotting the graph
########################################################
'''
# Convert PriYear to integer explicitly and handle potential errors
df_filtered['PriYear'] = pd.to_numeric(
    df_filtered['PriYear'], errors='coerce').fillna(0).astype(int)

# Drop rows where PriYear is 0 (unparsable) or MainIPC is missing
df_filtered = df_filtered[(df_filtered['PriYear'] > 0)
                          & df_filtered['MainIPC'].notna()]

# Step 1: Create a ranking of the 20 most frequent MainIPC codes

# Eliminate certain IPC codes from the analysis
#
# df_filtered = df[~df['MainIPC'].isin(['E04Y', 'A01x'])]

ipc_counts = df_filtered['MainIPC'].value_counts()
print("Top 20 IPCs by Frequency:")
print(ipc_counts.head(20))  # Display the top 20 IPCs

# Select the top_n IPC codes

top_n = 6
top_ipcs = ipc_counts.head(top_n).index

# Step 2: Create a DataFrame to count patents per year per IPC
year_range = range(2007, 2023)
ipc_yearly_counts = pd.DataFrame(index=top_ipcs, columns=year_range, data=0)

# Fill in the counts
for ipc in top_ipcs:
    ipc_data = df_filtered[df_filtered['MainIPC'] == ipc]
    yearly_counts = ipc_data['PriYear'].value_counts()
    for year in year_range:
        ipc_yearly_counts.at[ipc, year] = yearly_counts.get(year, 0)

# Step 3: Normalize data for plotting
normalized_data = ipc_yearly_counts.div(ipc_yearly_counts.max(axis=1), axis=0)

# Step 4: Create a parallel coordinates plot
fig, host = plt.subplots(figsize=(12, 8))

colors = plt.cm.tab10.colors

custom_colors = {
    'A61B': 'red',
    'G16H': 'lightgreen',
    'H04W': 'sienna',
    'G06F': 'darkgreen',
    'H04L': 'cyan',
    'H04N': 'blue'
}


for i, ipc in enumerate(top_ipcs):
    data = normalized_data.loc[ipc].values
    verts = list(zip(
        np.linspace(0, len(year_range) - 1, len(year_range)),
        data
    ))
    codes = [Path.MOVETO] + [Path.LINETO] * (len(verts) - 1)
    path = Path(verts, codes)

    # Use custom color if specified, otherwise default
    edgecolor = custom_colors.get(ipc, colors[i % len(colors)])

    patch = patches.PathPatch(path, facecolor='none',
                              lw=6, edgecolor=edgecolor)
    host.add_patch(patch)

# Formatting axes
host.set_xlim(0, len(year_range) - 1)
host.set_xticks(range(len(year_range)))
host.set_xticklabels(year_range, fontsize=10, rotation=45)
host.set_title(
    'Parallel Coordinates Plot: Top {} IPC Codes (2007-2022)'.format(top_n), fontsize=16)
host.set_xlabel('Year')
host.set_ylabel('Normalized Patent Counts')

# Adding legend
plt.legend(top_ipcs, title='Main IPC',
           bbox_to_anchor=(1.05, 1), loc='upper left')

plt.tight_layout()
plt.show()
