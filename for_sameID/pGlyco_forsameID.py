import pandas as pd
import re


def reorder_composition(comp):
    parts = re.findall(r'([A-Z])\((\d+)\)', comp)
    if parts:
        order = {'N': 1, 'H': 2, 'F': 3, 'A': 4, 'S': 5}
        sorted_parts = sorted(parts, key=lambda x: order.get(x[0], 999))
        return ''.join(f'{letter}({number})' for letter, number in sorted_parts)
    return comp

def rename_sugars(comp):
    sugar_names = {
        'H(': 'Hex(',
        'N(': 'HexNAc(',
        'F(': 'Fuc(',
        'A(': 'NeuAc('
    }
    for old, new in sugar_names.items():
        comp = comp.replace(old, new)
    return comp

def extract_accession_number(text):
    match = re.search(r'\|(.*?)\|', text)
    return match.group(1) if match else ''



input_file = 'pGlyco_forsameIDs_test.tsv'
df = pd.read_csv(input_file, sep='\t')


df['Comp1'] = df['GlycanComposition'].apply(reorder_composition)
df['Comp'] = df['Comp1'].apply(rename_sugars)


df['Accession number'] = df['Proteins'].apply(extract_accession_number)

df['Peptide'] = df['Peptide'].str.replace('J', 'N')


df['ID'] = df['Accession number'] + '_' + df['Peptide'] + '_' + df['GlySite'].astype(str) + '_' + df['Comp']


columns = ['ID'] + [col for col in df.columns if col != 'ID']
df = df[columns]

df.to_csv('pGlyco_forsameIDs_test_output.tsv', sep='\t',index=False)