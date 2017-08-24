# Performs a simple device inquiry, and returns a list of ble advertizements 
# discovered device

# NOTE: Python's struct.pack() will add padding bytes unless you make the endianness explicit. Little endian
# should be used for BLE. Always start a struct.pack() format string with "<"

import os
import sys
import struct
import bluetooth._bluetooth as bluez

LE_META_EVENT = 0x3e
LE_PUBLIC_ADDRESS=0x00
LE_RANDOM_ADDRESS=0x01
LE_SET_SCAN_PARAMETERS_CP_SIZE=7
OGF_LE_CTL=0x08
OCF_LE_SET_SCAN_PARAMETERS=0x000B
OCF_LE_SET_SCAN_ENABLE=0x000C
OCF_LE_CREATE_CONN=0x000D

LE_ROLE_MASTER = 0x00
LE_ROLE_SLAVE = 0x01

# these are actually subevents of LE_META_EVENT
EVT_LE_CONN_COMPLETE=0x01
EVT_LE_ADVERTISING_REPORT=0x02
EVT_LE_CONN_UPDATE_COMPLETE=0x03
EVT_LE_READ_REMOTE_USED_FEATURES_COMPLETE=0x04

# Advertisment event types
ADV_IND=0x00
ADV_DIRECT_IND=0x01
ADV_SCAN_IND=0x02
ADV_NONCONN_IND=0x03
ADV_SCAN_RSP=0x04


def hci_enable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x01)

def hci_disable_le_scan(sock):
    hci_toggle_le_scan(sock, 0x00)

def hci_toggle_le_scan(sock, enable):
    cmd_pkt = struct.pack("<BB", enable, 0x00)
    bluez.hci_send_cmd(sock, OGF_LE_CTL, OCF_LE_SET_SCAN_ENABLE, cmd_pkt)


def hci_le_set_scan_parameters(sock):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    SCAN_RANDOM = 0x01
    OWN_TYPE = SCAN_RANDOM
    SCAN_TYPE = 0x01


    
def parse_events(sock, loop_count=100):
    old_filter = sock.getsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, 14)

    # perform a device inquiry on bluetooth device #0
    # The inquiry should last 8 * 1.28 = 10.24 seconds
    # before the inquiry is performed, bluez should flush its cache of
    # previously discovered devices
    flt = bluez.hci_filter_new()
    bluez.hci_filter_all_events(flt)
    bluez.hci_filter_set_ptype(flt, bluez.HCI_EVENT_PKT)
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, flt )
    done = False
    results = []
    url=[]
    schemes=["http://www.","https://www.","http://","https://"]

    extensions = [ ".com/", ".org/", ".edu/", ".net/", ".info/", ".biz/", ".gov/",".com", ".org", ".edu", ".net", ".info", ".biz", ".gov" ]

    for i in range(0, loop_count):
        pkt = sock.recv(255)
        ptype, event, plen = struct.unpack("BBB", pkt[:3])
        #print "--------------" 
        if event == bluez.EVT_INQUIRY_RESULT_WITH_RSSI:
		i =0
        elif event == bluez.EVT_NUM_COMP_PKTS:
                i =0 
        elif event == bluez.EVT_DISCONN_COMPLETE:
                i =0 
        elif event == LE_META_EVENT:
            subevent, = struct.unpack("B", pkt[3])
            pkt = pkt[4:]
            if subevent == EVT_LE_CONN_COMPLETE:
                le_handle_connection_complete(pkt)
            elif subevent == EVT_LE_ADVERTISING_REPORT:
                #print "advertising report"
                num_reports = struct.unpack("B", pkt[0])[0]
                report_pkt_offset = 0
                done = True
		j=0
		packet=[]
		packet1=[]
		recognized_packet=['b827eb76639b']
		while j < len(pkt):
			packet1.append(ord(pkt[j]))
			j+=1
		
		packet=map(lambda x: "%02x" % x,packet1)
		
		packet_str=' '.join(packet)
		print 'Packet: ' + packet_str
		bd_addr=[]
		k=8
		
		while k > 2:
			bd_addr.append(packet[k])
                	k=k-1
      
		bd_addr_str=''.join(bd_addr)
                print 'HW addr :'+ bd_addr_str

	
		if bd_addr_str==recognized_packet[0]:
			print 'Recognized Beacon'
		#	print 'rssi packet :' , packet1[33]	

			rssi=256 - packet1[33]
			rssi=0 - rssi
			print 'RSSI : ' ,  rssi
	
				
			if packet[21]=='10':
				print 'Eddystone Url packet'
				url.append(schemes[packet1[23]])
				m=24
				while(packet1[m]>14):
					url.append(chr(packet1[m]))
					m=m+1
				url.append(extensions[packet1[m]])
		
				url_str=''.join(url)
				print 'Url : '+ url_str				
			elif packet[21]=='20':
				print 'Eddystone TLM packet'
				print 'Temp: ' , packet1[23]
				print 'Humidity: ' , packet1[25]
			else:
				print 'Unrecognized packet format'
		else:
			print 'Unrecognized Beacon'
			
		print("----------------------------------------------------------------------------------------------------------------")
		packet=[0]
		packet1=[0]
		url=[]
    sock.setsockopt( bluez.SOL_HCI, bluez.HCI_FILTER, old_filter )
