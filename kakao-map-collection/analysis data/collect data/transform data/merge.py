import pandas as pd
import os
from tqdm import tqdm

path = "og data/"
filepath = os.listdir(path)
merged_df = pd.DataFrame()
for file in tqdm(filepath):
    df = pd.read_excel(path + file)
    merged_df = merged_df.append(df)