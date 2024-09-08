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

print(final_out_map)