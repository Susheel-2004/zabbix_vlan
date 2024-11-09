import zapi
import pandas as pd
import numpy as np
from datetime import datetime
from collections import defaultdict
import requests
import json


def get_group(HOST_GROUP_NAME):
    host_group_params = {
    'filter': {'name': [HOST_GROUP_NAME]},
    'output': ['groupid']
    }
    host_group_response = zapi.zabbix_api('hostgroup.get', host_group_params)
    
    return host_group_response

def get_hosts(HOST_GROUP_NAME):
    host_group_id = get_group(HOST_GROUP_NAME)['result'][0]['groupid']
    host_params = {
        'groupids': host_group_id,
        'output': ['hostid', 'host'],
        'selectInterfaces': ['interfaceid', 'ip']
    }
    host_response = zapi.zabbix_api('host.get', host_params)
    d = {}
    for i in host_response['result']:
        d[i['hostid']] = i['host']
    return d

def get_interfaces(hostid):
    interface_params = {
        "output" : "extend",
        "hostids" : hostid
    }
    interfaces = zapi.zabbix_api("hostinterface.get", interface_params)
    df = pd.DataFrame(interfaces['result'])
    return interfaces

def get_items(hostids, inout="default", common=False):
    key = [f"net.if.in[ifHCINOctets", f"net.if.out[ifHCOUTOctets"]
    if inout == 'in' or inout == 'out':
        key = f"net.if.{inout}[ifHC{inout.upper()}Octets"
    item_params = {
        "output": "extend",
            "hostids":[hostids],
            "with_triggers": True,
            "search": {
                "key_": key
                # [ifHCInOctets.98]"
            },
            "sortfield": "name"
    }
    items = zapi.zabbix_api("item.get", item_params)
    if items['result'] == []:
        return None
    df = pd.DataFrame(items['result'])
    df = df[['itemid', 'name', 'hostid']]
    if (common):
        df['name'] = df['name'].str.split(":", expand=True)[0]
        df = df.rename(columns={'itemid' : f"itemid_{inout}"})
    return df

def get_history(itemids):
    history_params = {
        'output': 'extend',
        'history': 3,
        'itemids': itemids,
        'sortfield': 'clock',
        'sortorder': 'DESC',
        "time_from": int(datetime.now().timestamp()) - 3600,
        'time_till': int(datetime.now().timestamp())
    }
    history = zapi.zabbix_api('history.get', history_params)
    df = pd.DataFrame(history['result'])
    return df[['itemid', 'clock', 'value']]

def get_trend(itemid, TIME_PERIOD):
    params = {
        "output": "extend",
        "itemids": itemid,
        "time_from": int(datetime.now().timestamp()) - 3600*TIME_PERIOD,
        "time_till": int(datetime.now().timestamp())
    }
    trend = zapi.zabbix_api("trend.get", params)
    df = pd.DataFrame(trend['result'])
    return df

def get_final_df(hosts, inout):
    TIME_PERIOD = 169
    for i in list(hosts):
        if hosts[i] == None:
            del hosts[i]

    host_item_map = {}
    for i in hosts:
        host_item_map[i] = get_items(i, inout) 
    # print(host_in_item_map)
    host_item_map = {k: v for k, v in host_item_map.items() if v is not None}
    host_final_map = {}
    for i in host_item_map:
        df = pd.DataFrame(columns=['itemid', 'name', 'value_max', 'value_min', 'value_avg'])
        for item in host_item_map[i].itertuples():
            trend = get_trend(item.itemid, TIME_PERIOD)
            if 'value_min' in trend and 'value_max' in trend and 'value_avg' in trend: 
                value_min = trend['value_min'].astype('float').min()/1000000
                value_max = trend['value_max'].astype('float').max()/1000000
                value_avg = trend['value_avg'].astype('float').mean()/1000000
                name = item.name.split(':')[0]
                df.loc[len(df)]= (item.itemid, name, value_max, value_min, value_avg)
        host_final_map[i] = df
    return host_final_map
# print(get_trend(75796)['value_min'].astype('float').min())


def get_topTalkers(HOST_GROUP_NAME):
    hosts = get_hosts(HOST_GROUP_NAME)
    for i in list(hosts):
        if hosts[i] == None:
            del hosts[i]
    sent = []
    received = []
    for i in hosts:
        received.append(get_items(i, "in", True))
        sent.append(get_items(i, "out", True))
    dfs = []
    new_columns = ["max_bits_received", "min_bits_received", "max_bits_sent", "min_bits_sent"]
    for i in range(len(hosts)):
        dfs.append(pd.merge(sent[i], received[i], on='name', how="inner"))
        dfs[i] = dfs[i][["name", "itemid_in", "itemid_out", "hostid_x"]]
    for df in dfs:
        for col in new_columns: df[col] = None
        for index, elem in df.iterrows():
            trend_in = get_trend(elem.itemid_in, 25)
            trend_out = get_trend(elem.itemid_out, 25)
            if 'value_min' in trend_in and 'value_max' in trend_in:
                value_min = trend_in['value_min'].astype('float').min()/1000000
                value_max = trend_in['value_max'].astype('float').max()/1000000
                df.at[index, 'max_bits_received'] = value_max
                df.at[index, 'min_bits_received'] = value_min
            if 'value_min' in trend_out and 'value_max' in trend_out:
                value_min = trend_out['value_min'].astype('float').min()/1000000
                value_max = trend_out['value_max'].astype('float').max()/1000000
                df.at[index, 'max_bits_sent'] = value_max
                df.at[index, 'min_bits_sent'] = value_min
    for df in dfs: df.drop(columns=['itemid_in', "itemid_out"], inplace=True)
    for df in dfs:
        filename = hosts[df['hostid_x'].iloc[0]]
        df.drop(columns=['hostid_x'], inplace=True)
        # Sort by 'max_bits_received' and 'max_bits_sent' in descending order
        sorted_df = df.sort_values(by=['max_bits_received', 'max_bits_sent'], ascending=[False, False])
        sorted_df[new_columns] = sorted_df[new_columns].round(4)
        sorted_df[new_columns] = sorted_df[new_columns].apply(lambda x: x.astype(str) + " Mb/s")

        sorted_df.head(10).to_csv(f"{filename}.csv", index=False)
    

    