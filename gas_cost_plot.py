import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression

columns = ["function_name", "gas_cost", "user_id", "block_number"]

## ANALYSE FOR 4 GROUP MEMBER
file_path = "client/gas_cost/gas_cost_4.csv"
df = pd.read_csv(file_path, names=columns)

# list of function
fun_list = df.function_name.unique()

N_fun = len(df.function_name.unique())

# group_size computation
group_size = len(df.user_id.unique())
group = list(df.user_id.unique())

# associate round to each function
df['round'] = 0
for user in group:
    for fun in fun_list:
        df.loc[(df['user_id']==user) & (df['function_name']==fun),'round'] = range(len(df[(df['user_id']==user) & (df['function_name']==fun)]))
pd.set_option('display.max_rows', None)

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

# stats gas cumul
df.sort_values(by="block_number", inplace=True)

mapping = {
    "group_creation":"initialisation",
    "publish_tpk":"initialisation",
    "encrypt_shares":"initialisation",
    "publish_group_key":"initialisation",
    "send_file":"encryption",
    "send_share":"decryption"
}
df['phase'] = df['function_name'].map(mapping)
df['cumul_gas_cost'] = df['gas_cost'].cumsum()

df.plot("block_number", "cumul_gas_cost",ax=ax[1,1])
for r in df['round'].unique():
    min_block = df[(df['round']==r) & (df['phase']=='initialisation')]['block_number'].min()
    max_block = df[(df['round']==r) & (df['phase']=='initialisation')]['block_number'].max()
    ax[1,1].axvspan(min_block,max_block,fill=False, alpha=0.5, label="_"*int(r)+"initialisation", hatch=".")

    min_block = df[(df['round']==r) & (df['phase']=='encryption')]['block_number'].min()
    max_block = df[(df['round']==r) & (df['phase']=='encryption')]['block_number'].max()
    ax[1,1].axvspan(min_block,max_block,color="black", alpha=0.5, label="_"*int(r)+"encryption")

    min_block = df[(df['round']==r) & (df['phase']=='decryption')]['block_number'].min()
    max_block = df[(df['round']==r) & (df['phase']=='decryption')]['block_number'].max()
    ax[1,1].axvspan(min_block,max_block,fill=False, alpha=0.5,label="_"*int(r)+"decryption",hatch="//")

ax[0,0].legend()
ax[1,0].legend()
ax[0,1].legend()
ax[1,1].legend()

## ANALYSE FOR DIFFERENT SIZE OF GROUP
# creation des dataframe
file_path_2 = "client/gas_cost/gas_cost_2.csv"
df_2 = pd.read_csv(file_path_2, names=columns)
file_path_4 = "client/gas_cost/gas_cost_4.csv"
df_4 = pd.read_csv(file_path_4, names=columns)
file_path_6 = "client/gas_cost/gas_cost_6.csv"
df_6 = pd.read_csv(file_path_6, names=columns)
file_path_10 = "client/gas_cost/gas_cost_10.csv"
df_10 = pd.read_csv(file_path_10, names=columns)

list_df = [(2,df_2),(4,df_4),(6,df_6),(10,df_10)]

# associate round to each function
for i,df in list_df:
    group_size = len(df.user_id.unique())
    group = list(df.user_id.unique())

    df['round'] = 0
    for user in group:
        for fun in fun_list:
            df.loc[(df['user_id']==user) & (df['function_name']==fun),'round'] = range(len(df[(df['user_id']==user) & (df['function_name']==fun)]))

df_2['client_number'] = 2
df_4['client_number'] = 4
df_6['client_number'] = 6
df_10['client_number'] = 10

df = pd.concat([df_2, df_4, df_6, df_10])
df = df.groupby(['client_number', 'round', 'function_name']).mean().drop(columns=['block_number']).reset_index()
# analyse round 0
round_0 = df[df['round']==0].drop(columns='round').groupby(['client_number','function_name']).mean().unstack(level=1)['gas_cost']
round_0.plot.bar()
plt.title('Gas cost of transaction for the first file')
round_0.plot(marker='o', linestyle=' ',title="Gas cost of transaction for the first file")

linear_regressor = LinearRegression()
linear_regressor.fit(np.array(round_0.index).reshape((-1,1)), round_0['group_creation'])
x=np.linspace(0,10,100)
y = linear_regressor.predict(x.reshape(-1,1))
plt.plot(x,y, label='a0={:.0f} a1={:.0f}'.format(linear_regressor.intercept_, linear_regressor.coef_[0]))
plt.legend()

linear_regressor = LinearRegression()
linear_regressor.fit(np.array(round_0.index).reshape((-1,1)), round_0['encrypt_shares'])
x=np.linspace(0,10,100)
y = linear_regressor.predict(x.reshape(-1,1))
plt.plot(x,y, label='a0={:.0f} a1={:.0f}'.format(linear_regressor.intercept_, linear_regressor.coef_[0]))
plt.legend()

# analyse round 1
round_1 = df[df['round']==1].drop(columns='round').groupby(['client_number','function_name']).mean().unstack(level=1)['gas_cost']
round_1.plot.bar()
plt.title('Gas cost of transaction for the second file')
round_1.plot(marker='o', linestyle=' ',title="Gas cost of transaction for the first file")

linear_regressor = LinearRegression()
linear_regressor.fit(np.array(round_1.index).reshape((-1,1)), round_1['encrypt_shares'])
x=np.linspace(0,10,100)
y = linear_regressor.predict(x.reshape(-1,1))
plt.plot(x,y, label='a0={:.0f} a1={:.0f}'.format(linear_regressor.intercept_, linear_regressor.coef_[0]))
plt.legend()

plt.show()
