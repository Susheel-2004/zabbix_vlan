import csv
import methods

def get_bits_sent(host_group_name):
    hosts = methods.get_hosts(host_group_name)
    final_out_map = methods.get_final_df(hosts, "out")
    for i in hosts:
        if i in final_out_map:
            with open(f"{hosts[i]}_bits_sent.csv" , "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(['Interface : Bits Sent', 'MAX', 'MIN', 'AVERAGE'])
                for item in final_out_map[i].itertuples():
                    writer.writerow([item.name, str(round(item.value_max, 4)) + " Mb/s", str(round(item.value_min, 4)) + " Mb/s", str(round(item.value_avg, 4)) + " Mb/s"])

if __name__ == "__main__":
    get_bits_sent()