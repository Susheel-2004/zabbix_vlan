import zapi
import pandas as pd
import numpy as np
from datetime import datetime
import requests
import json

# HOST_GROUP_NAME = "Network Devices"
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

def get_items(hostids, inout):
    item_params = {
        "output": "extend",
            "hostids": [hostids],
            "with_triggers": True,
            "search": {
                "key_": f"net.if.{inout}[ifHC{inout.upper()}Octets"
                # [ifHCInOctets.98]"
            },
            "sortfield": "name"
    }
    items = zapi.zabbix_api("item.get", item_params)
    if items['result'] == []:
        return None
    df = pd.DataFrame(items['result'])
    df = df[['itemid', 'name', 'hostid']]
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

def get_trend(itemid):
    params = {
        "output": "extend",
        "itemids": itemid,
        "time_from": int(datetime.now().timestamp()) - 3600*25,
        "time_till": int(datetime.now().timestamp())
    }
    trend = zapi.zabbix_api("trend.get", params)
    df = pd.DataFrame(trend['result'])
    return df

def get_final_df(hosts, inout):
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
            trend = get_trend(item.itemid)
            if 'value_min' in trend and 'value_max' in trend and 'value_avg' in trend: 
                value_min = trend['value_min'].astype('float').min()/1000
                value_max = trend['value_max'].astype('float').max()/1000
                value_avg = trend['value_avg'].astype('float').mean()/1000
                name = item.name.split(':')[0]
                df.loc[len(df)]= (item.itemid, name, value_max, value_min, value_avg)
        host_final_map[i] = df
    return host_final_map
# print(get_trend(75796)['value_min'].astype('float').min())