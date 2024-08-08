from netmiko import ConnectHandler
from log import authLog

import traceback
import csv
import os

shHostname = "show run | i hostname"
shRunAicinfo = "show run | inc aicinfo"
snmpComnt = "snmp-server community aicinfo RO 99"

deviceList = []

def snmpComntCheck(validIPs, username, netDevice):
    # This function is test the connectivity to the INET network of the Opengear devices

    for validDeviceIP in validIPs:
        try:
            validDeviceIP = validDeviceIP.strip()
            currentNetDevice = {
                'device_type': 'cisco_xe',
                'ip': validDeviceIP,
                'username': username,
                'password': netDevice['password'],
                'secret': netDevice['secret'],
                'global_delay_factor': 2.0,
                'timeout': 120,
                'session_log': 'netmikoLog.txt',
                'verbose': True,
                'session_log_file_mode': 'append'
            }

            print(f"Connecting to device {validDeviceIP}...")
            with ConnectHandler(**currentNetDevice) as sshAccess:
                try:
                    sshAccess.enable()
                    shHostnameOut = sshAccess.send_command(shHostname)
                    authLog.info(f"User {username} successfully found the hostname {shHostnameOut}")
                    shHostnameOut = shHostnameOut.split(' ')[1]
                    shHostnameOut = shHostnameOut + "#"
                    print(f"INFO: This is the hostname: {shHostnameOut}")

                    print(f"INFO: Taking a \"{shRunAicinfo}\" for device: {validDeviceIP}")
                    shRunAicinfoOut = sshAccess.send_command(shRunAicinfo)
                    authLog.info(f"Automation successfully ran the command:{shRunAicinfo}\n{shHostnameOut}{shRunAicinfo}\n{shRunAicinfoOut}")

                    if snmpComnt in shRunAicinfoOut:
                        print(f"INFO: {snmpComnt} was found under device {validDeviceIP}")
                        authLog.info(f"{snmpComnt} was found under device {validDeviceIP}")
                        deviceList.append(validDeviceIP)
                    else:
                        authLog.info(f"{snmpComnt} was not found under device {validDeviceIP}")

                except Exception as error:
                    print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
                    authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
                    authLog.error(traceback.format_exc(),"\n")
                    os.system("PAUSE")
       
        except Exception as error:
            print(f"ERROR: An error occurred: {error}\n", traceback.format_exc())
            authLog.error(f"User {username} connected to {validDeviceIP} got an error: {error}")
            authLog.error(traceback.format_exc(),"\n")
            with open(f"failedDevices.txt","a") as failedDevices:
                failedDevices.write(f"User {username} connected to {validDeviceIP} got an error.\n")
        
        finally:
            print(f"Outputs and files successfully created for device {validDeviceIP}")
            print("For any erros or logs please check Logs -> authLog.txt\n")

    with open('Outputs/Devices with community abc.csv', mode='a', newline='') as file:
        authLog.info(f"File Devices with community abc.csv was created successfully")
        writer = csv.writer(file)
        for item in deviceList:
            writer.writerow([item])