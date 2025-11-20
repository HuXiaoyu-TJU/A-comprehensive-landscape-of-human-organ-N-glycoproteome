import pandas as pd
import re
import time


start_time = time.time()

input_file = 'Glyco-Decipher_forsameIDs_test.tsv'
df = pd.read_csv(input_file, sep='\t')
initial_rows = len(df)

print(f"start: {input_file}")


df['Accession number'] = df['Protein'].str.extract(r'\|(.*?)\|')



def extract_glycosite(peptide):
    n_positions = [i for i, char in enumerate(peptide) if char == 'N']
    if len(n_positions) == 1:
        return n_positions[0] + 1  
    elif len(n_positions) > 1:
        for pos in n_positions:
            if pos + 2 < len(peptide) and peptide[pos+1] != 'P' and peptide[pos+2] in ['S', 'T', 'C']:
                return pos + 1
        return n_positions[0] + 1
    return None

df['Glycosite'] = df['Peptide'].apply(extract_glycosite)


def adjust_glycan_comp(comp):
    parts = re.findall(r'([A-Za-z]+)\((\d+)\)', comp)
    if parts:
        order = {'HexNAc': 1, 'Hex': 2, 'Fuc': 3, 'NeuAc': 4}
        sorted_parts = sorted(parts, key=lambda x: order.get(x[0], 999))
        return ''.join(f'{sugar}({number})' for sugar, number in sorted_parts)
    return comp

df['Comp'] = df['GlycanComposition'].apply(adjust_glycan_comp)


df['ID'] = df['Accession number'] + '_' + df['Peptide'] + '_' + df['Glycosite'].astype(str) + '_' + df['Comp']


cols = df.columns.tolist()
cols = ['ID'] + [col for col in cols if col != 'ID']
df = df[cols]


output_file = 'Glyco-Decipher_forsameIDs_test_output.tsv'
df.to_csv(output_file, sep='\t', index=False)


end_time = time.time()


run_time = end_time - start_time


print(f"Complete.")
print(f"run time: {run_time:.2f} 秒")
print(f"files saved: {output_file}")