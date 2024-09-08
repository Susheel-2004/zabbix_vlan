import csv
import methods

def get_bits_received(host_group_name):
    hosts = methods.get_hosts(host_group_name)
    final_in_map = methods.get_final_df(hosts, "in")
    with open("bits_received.csv" , "w", newline="") as f:
        writer = csv.writer(f)
        for i in hosts:
            if i in final_in_map:
                writer.writerow([hosts[i]])
                writer.writerow(['Interface : Bits Received', 'MIN(KBPS)', 'MAX(KBPS)', 'AVERAGE(KBPS)'])
                for item in final_in_map[i].itertuples():
                    writer.writerow([item.name, item.value_min, item.value_max, item.value_avg])

if __name__ == "__main__":
    get_bits_received()