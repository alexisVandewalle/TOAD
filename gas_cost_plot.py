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
init = df.drop(columns=['send_file','send_share'])
init_stats = init.groupby(["round", 'function_name']).mean()
init_stats.rename(columns={"gas_cost":"gas_cost_mean"}, inplace=True)
init_stats['gas_cost_max'] = init.groupby(["round", 'function_name']).max()['gas_cost']
init_stats['gas_cost_min'] = init.groupby(["round", 'function_name']).min()['gas_cost']



_, ax = plt.subplots(2,2)
init_stats.loc[0].gas_cost_max.plot(kind='bar', label="gas cost max", color="none",edgecolor="red", ax=ax[0,0],rot=0)
init_stats.loc[0].gas_cost_mean.plot(kind='bar', label="gas cost mean", color='green', ax=ax[0,0],rot=0)
init_stats.loc[0].gas_cost_min.plot(kind='bar', label="gas cost min", color="none", edgecolor="blue", ax=ax[0,0],rot=0)
ax[0,0].set_title("initialisation cost - first file")

init_stats.loc[1].gas_cost_max.plot(kind='bar', label="gas cost max", color="none",edgecolor="red", ax=ax[1,0],rot=0)
init_stats.loc[1].gas_cost_mean.plot(kind='bar', label="gas cost mean", color='green', ax=ax[1,0],rot=0)
init_stats.loc[1].gas_cost_min.plot(kind='bar', label="gas cost min", color="none", edgecolor="blue", ax=ax[1,0],rot=0)
ax[1,0].set_title("initialisation cost - next file")
ax[0,0].legend()
ax[1,0].legend()
plt.show()
