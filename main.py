import requests
import json
import zapi
import methods
import pandas as pd

HOST_GROUP_NAME = "Network Devices"
TIME_PERIOD = 2 * 3600 #seconds

hosts = methods.get_hosts(HOST_GROUP_NAME)

final_in_map = methods.get_final_df(hosts, "in")
final_out_map = methods.get_final_df(hosts, "out")

# remove host with none
# for i in list(hosts):
#     if hosts[i] == None:
#         del hosts[i]

# host_in_item_map = {}
# host_out_item_map = {}
# for i in hosts:
#     host_in_item_map[i] = methods.get_items(i, "in") 
#     host_out_item_map[i] = methods.get_items(i, "out")
# # print(host_in_item_map)
# host_in_item_map = {k: v for k, v in host_in_item_map.items() if v is not None}
# host_out_item_map = {k: v for k, v in host_out_item_map.items() if v is not None}
# host_final_map = {}
# for i in host_in_item_map:
#     df = pd.DataFrame(columns=['itemid', 'name', 'value_max', 'value_min', 'value_avg'])
#     for item in host_in_item_map[i].itertuples():
#         trend = methods.get_trend(item.itemid)
#         if 'value_min' in trend and 'value_max' in trend and 'value_avg' in trend: 
#             value_min = trend['value_min'].astype('float').min()/1000
#             value_max = trend['value_max'].astype('float').max()/1000
#             value_avg = trend['value_avg'].astype('float').mean()/1000
#             name = item.name
#             df.loc[len(df)]= (item.itemid, name, value_max, value_min, value_avg)
#     host_final_map[i] = df
print(final_out_map)

# trend = methods.get_trend(75796)
# trend.to_csv("trend.csv")
# condensed = [trend['value_avg'].astype(float).mean(), trend['value_min'].astype(float).min(), trend['value_max'].astype(float).max()]
# print(condensed)