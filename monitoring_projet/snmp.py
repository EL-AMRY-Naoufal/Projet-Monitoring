from pysnmp.hlapi import *
import socket

class SNMPMonitor:
    def __init__(self, target_ip, community_string):
        self.target_ip = target_ip
        self.community_string = community_string

    def snmp_get(self, oid):
        errorIndication, errorStatus, errorIndex, varBinds = next(
            getCmd(SnmpEngine(),
                   CommunityData(self.community_string),
                   UdpTransportTarget((self.target_ip, 161)),
                   ContextData(),
                   ObjectType(ObjectIdentity(oid)))
        )

        if errorIndication:
            print(f"Error: {errorIndication}")
            return None
        elif errorStatus:
            print(f"Error: {errorStatus}")
            return None
        else:
            return varBinds[0][1].prettyPrint()

   

        # Extracting the second number from the SNMP response
        if result and len(result) >= 2:
            second_number = result[1][1]  # Assuming there are at least two elements in the result
            return second_number
        else:
            print("Insufficient data received.")
            return None


    def get_memory_usage(self):
        memory_oid = '1.3.6.1.2.1.25.2.3.1.5.1'   # Example OID for memory usage
        return self.snmp_get(memory_oid)

    def get_cpu_load(self):
        cpu_oid = '1.3.6.1.4.1.311.1.1.3.1.1.2.1.3'    # Example OID for CPU load
        return self.snmp_get(cpu_oid)

    def get_disk_space(self):
        disk_oid = '1.3.6.1.2.1.25.2.3.1.6.1'   # Example OID for disk space
        return self.snmp_get(disk_oid)

    def get_adressIp(self):
        hostname = socket.gethostname()
        adressIp = socket.gethostbyname(hostname)
        return adressIp
    

# Example usage
if __name__ == "__main__":
    # SNMP settings

    
    target_ip = '127.0.0.1'
    community_string = 'public'


    # Create SNMPMonitor instance
    snmp_monitor = SNMPMonitor(target_ip, community_string)

    print(snmp_monitor.get_adressIp())
    # Get SNMP information
    memory_usage = snmp_monitor.get_memory_usage()
    cpu_load = snmp_monitor.get_cpu_load()
    disk_space = snmp_monitor.get_disk_space()


    print("Memory Usage:", memory_usage)
    print("CPU Load:", cpu_load)
    print("Disk Space:", disk_space)