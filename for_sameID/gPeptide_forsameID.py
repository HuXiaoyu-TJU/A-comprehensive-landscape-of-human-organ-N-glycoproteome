import pandas as pd
import re
import time



start_time = time.time()


input_file = 'gPeptide_forsameID_test.tsv'
df = pd.read_csv(input_file, sep='\t')


def process_composition(comp):
    return re.sub(r'[FS]0', '', comp)

df['Comp1'] = df['Composition'].apply(process_composition)


def replace_comp(comp):
    replacements = {
        'H': ')Hex(',
        'N': 'HexNAc(',
        'F': ')Fuc(',
        'S': ')NeuAc('
    }
    for old, new in replacements.items():
        comp = comp.replace(old, new)
    return comp + ')'

df['Comp'] = df['Comp1'].apply(replace_comp)


def extract_glycosite(ptm):
    match = re.search(r'(\d+)GlcNAc', ptm)
    return match.group(1) if match else ''

df['Glycosite'] = df['p-PTMs'].apply(extract_glycosite)


df['ID'] = df['Accession Number'] + '_' + df['p-Seq.'] + '_' + df['Glycosite'] + '_' + df['Comp']


cols = df.columns.tolist()
cols = ['ID'] + [col for col in cols if col != 'ID']
df = df[cols]


df.to_csv('gPeptide_forsameID_test_output.tsv', sep='\t', index=False)


