import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


file_path = "client/gas_cost/gas_cost.csv"
columns = ["function_name", "gas_cost", "user_id"]
df = pd.read_csv(file_path, names=columns)

# list of function
print("list of functions:")
fun_list = df.function_name.unique()
print(fun_list)

print("number of functions:")
N_fun = len(df.function_name.unique())
print(N_fun)

# group_size computation
group_size = len(df.user_id.unique())
group = list(df.user_id.unique())

# associate round to each function
df['round'] = 0
for user in group:
    for fun in fun_list:
        df.loc[(df['user_id']==user) & (df['function_name']==fun),'round'] = range(len(df[(df['user_id']==user) & (df['function_name']==fun)]))


# stats - min - mean - max init phase
init = df[(df['function_name']!='send_file') & (df['function_name']!='send_share')]
init_stats = init.groupby(["round", 'function_name']).mean()
init_stats.rename(columns={"gas_cost":"gas_cost_mean"}, inplace=True)
init_stats['gas_cost_max'] = init.groupby(["round", 'function_name']).max()['gas_cost']
init_stats['gas_cost_min'] = init.groupby(["round", 'function_name']).min()['gas_cost']



_, ax = plt.subplots(2,2)
init_stats.loc[0].gas_cost_max.plot(kind='bar', label="gas cost max", color="none",edgecolor="red", ax=ax[0,0],rot=0)
init_stats.loc[0].gas_cost_mean.plot(kind='bar', label="gas cost mean", color='#BADA55', ax=ax[0,0],rot=0)
init_stats.loc[0].gas_cost_min.plot(kind='bar', label="gas cost min", color="none", edgecolor="blue", ax=ax[0,0],rot=0)
ax[0,0].set_title("Initialisation cost by user- first file")

init_stats.loc[1].gas_cost_max.plot(kind='bar', label="gas cost max", color="none",edgecolor="red", ax=ax[1,0],rot=0)
init_stats.loc[1].gas_cost_mean.plot(kind='bar', label="gas cost mean", color='#BADA55', ax=ax[1,0],rot=0)
init_stats.loc[1].gas_cost_min.plot(kind='bar', label="gas cost min", color="none", edgecolor="blue", ax=ax[1,0],rot=0)
ax[1,0].set_title("Initialisation cost by user - next file")

# stats encryption - decryption
encrypt = df[(df['function_name']=='send_file') | (df['function_name']=='send_share')].drop(columns=['round'])
encrypt_stats = encrypt.groupby('function_name').mean()
encrypt_stats.rename(columns={"gas_cost":"gas_cost_mean"}, inplace=True)
encrypt_stats['gas_cost_max'] = encrypt.groupby('function_name').max()['gas_cost']
encrypt_stats['gas_cost_min'] = encrypt.groupby('function_name').min()['gas_cost']

encrypt_stats.gas_cost_max.plot(kind='bar', label="gas cost max", color="none",edgecolor="red", ax=ax[0,1],rot=0)
encrypt_stats.gas_cost_mean.plot(kind='bar', label="gas cost mean", color='#BADA55', ax=ax[0,1],rot=0)
encrypt_stats.gas_cost_min.plot(kind='bar', label="gas cost min", color="none", edgecolor="blue", ax=ax[0,1],rot=0)
ax[0,1].set_title("Encryption-decryption cost by user")

# stats gas cumul per round
cumul = df[(df['function_name']!='send_file') & (df['function_name']!="group_creation")]
cumul = cumul.groupby(["round","function_name"]).mean()
cumul = cumul.groupby('round').sum()
cumul = cumul.cumsum()
cumul.rename(columns={"gas_cost": "cumuled_gas_cost_per_file"}, inplace=True)

cumul.cumuled_gas_cost_per_file.plot(kind='bar', color='#BADA55', ax=ax[1,1], rot=0)
ax[1,1].set_title('Cumuled gas cost per file (without send_file and group_creation step)')

ax[0,0].legend()
ax[1,0].legend()
ax[0,1].legend()
plt.show()
