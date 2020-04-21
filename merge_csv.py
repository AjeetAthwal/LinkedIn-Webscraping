import pandas as pd
import numpy as np
import time
from pathlib import Path
from os.path import join

# Getdata from different directory
csv_dir = (Path(__file__).parent / "../../Data/LinkedIn").resolve()

# Get csv data of names and previous job titles to search on linkedin
old_csv_file =  'info.csv'
new_csv_file = 'new_'+old_csv_file
merged_csv_file = 'to_send_'+old_csv_file

old_csv = join(csv_dir,old_csv_file)
old_df = pd.read_csv(old_csv)

new_csv = join(csv_dir,new_csv_file)
new_df = pd.read_csv(new_csv)

merged_csv = join(csv_dir,merged_csv_file)

new_df = new_df.drop(['First Name','Last Name','Last Name Adj','Account Name'],axis=1)

merged_df = pd.concat([old_df,new_df],axis=1)

merged_df.to_csv(merged_csv , index=False)