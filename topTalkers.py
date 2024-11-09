import methods

HOST_GROUP_NAME = "Security Devices"
hosts = methods.get_hosts(HOST_GROUP_NAME)
print(hosts)