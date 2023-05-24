import pandas as pd
import numpy as np
import json

with open('statistics.json') as f:
    statistics = json.load(f)

with open('player_settings.json') as f:
    sett = json.load(f)


sid_list = []
for sid in sett.values():
    sid_list.append(sid["SID"])
biglist = []

for values in statistics.values():
    biglist.append(list(values.values()))
arraylist = np.array(biglist)
# print(arraylist)
# print(len(arraylist))
df = pd.DataFrame(arraylist,index=sid_list, columns=["game", "win", "lose", "ship"])
print("\ndefault view\n")
print(df)
df = df.sort_values(["game", "lose"], ascending=(False, True))
print("\nsorted by 'game' and filtered 'game > 0'\n")
print(df[df["game"]>0])
# df.to_excel("foo.xlsx", sheet_name="Sheet1")
