import sys, getopt
import pandas as pd
import os
import numpy
import matplotlib.pyplot as plt

def extract_flows(g):
   # Find the location of SYN packets
   is_syn = g['Info'].fillna('').str.contains('\[SYN\]')
   syn = g[is_syn].index.values

   # Find the location of the FIN-ACK packets
   is_finack = g['Info'].fillna('').str.contains('\[FIN, ACK\]')
   finack = g[is_finack].index.values

   # Loop over SYN packets
   runs = []
   for num, start in enumerate(syn, start=1):
       try:
           # Find the first FIN-ACK packet after each SYN packet
           #     If none, raises IndexError
           stop = finack[finack > start][0]
           runs.append([# The flow number counter
                        num,
                        # The time difference between the packets
                        g.loc[stop, 'Time'] - g.loc[start, 'Time'],
                        # The accumulated length
                        g.loc[start:stop, 'Length'].sum()])
       except IndexError:
           break

   # The output must be a DataFrame
   output = (pd.DataFrame(runs, columns=['Flow number', 'Time', 'Length'])
               .set_index('Flow number'))
   return output


def main(argv):
   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
   except getopt.GetoptError:
      print 'first.py -i <inputfile> -o <outputfile>'
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print 'test.py -i <inputfile> -o <outputfile>'
         sys.exit()
      elif opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg


   data = pd.read_csv(inputfile)

   # Get the base name to be used for log files
   base = os.path.splitext(inputfile)[0]

   #print len(data)
   #tcp_packets = data[data.Protocol == "TCP"]
   #udp_packets = data[data.Protocol == "UDP"]
   #http_packets = data[data.Protocol == "HTTP"]
   #arp_packets = data[data.Protocol == "ARP"]
   #icmp_packets = data[data.Protocol == "ICMP"]
   #dns_packets = data[data.Protocol == "DNS"]
   #ntp_packets = data[data.Protocol == "NTP"]
   #ssl_packets = data[data.Protocol == "SSL"]
   #ssh_packets = data[data.Protocol == "SSH"]
   #telnet_packets = data[data.Protocol == "TELNET"]

   #print "Trace name: ", inputfile
   #print "Total number of packets:  %d"% len(data)
   #print "# of TCP_PACKETS:  %d (%f%%)"% (len(tcp_packets), float(len(tcp_packets))/float(len(data))*100)
   #print "# of UDP_PACKETS:  %d (%f%%)"% (len(udp_packets), float(len(udp_packets))/float(len(data))*100)
   #print "# of HTTP_PACKETS: %d (%f%%)"% (len(http_packets), float(len(http_packets))/float(len(data))*100)
   #print "# of ARP_PACKETS:  %d (%f%%)"% (len(arp_packets), float(len(arp_packets))/float(len(data))*100)
   #print "# of ICMP_PACKETS:  %d (%f%%)"% (len(icmp_packets), float(len(icmp_packets))/float(len(data))*100)
   #print "# of DNS_PACKETS:  %d (%f%%)"% (len(dns_packets), float(len(dns_packets))/float(len(data))*100)
   #print "# of NTP_PACKETS:  %d (%f%%)"% (len(ntp_packets), float(len(ntp_packets))/float(len(data))*100)
   #print "# of SSL_PACKETS:  %d (%f%%)"% (len(ssl_packets), float(len(ssl_packets))/float(len(data))*100)
   #print "# of SSH_PACKETS:  %d (%f%%)"% (len(ssh_packets), float(len(ssh_packets))/float(len(data))*100)
   #print "# of TELNET_PACKETS:  %d (%f%%)"% (len(telnet_packets), float(len(telnet_packets))/float(len(data))*100)
   # 
   #uniqs = pd.unique(data.Source.ravel())
   #print uniqs
   #print len(uniqs) 

   #uniqd = pd.unique(data.Destination.ravel())
   #print uniqd
   #print len(uniqd) 

   #uniqi = numpy.unique(data[['Source', 'Destination']])	
   #print uniqi
   #print len(uniqi) 

   #uniqp = pd.unique(data.Protocol.ravel())
   #print uniqp
   #print len(uniqp) 

   #------------------------------------------------
   # CDF of the length of packets 

   length = data["Length"].sort_values()
   #print length
   length[len(length)] = length.iloc[-1]
   
   cum_dist = numpy.linspace(0.,1.,len(length))
   length_cdf = pd.Series(cum_dist, index=length)
   
 
   ax =length_cdf.plot(drawstyle='steps', title = "CDF of packet size for "+ base, grid=True)
   ax.set_xlim(right=1600)

   # setting xticks limits 
   #http://stackoverflow.com/questions/24943991/matplotlib-change-grid-interval-and-specify-tick-labels
   minor_ticks = numpy.arange(0, 1600, 20) 
   ax.set_xticks(minor_ticks, minor=True)
   
   ax.set_xlabel("Packet size (in bytes)")
   ax.set_ylabel("CDF")

   #plt.show()
   fig = ax.get_figure()
   fig.savefig(base+'_packet_size.jpg')


   #-----------------------------------------------
   #Protocol classification by Number of packets

   #http://stackoverflow.com/questions/37038733/adding-column-headers-to-new-pandas-dataframe?noredirect=1&lq=1 
   ptocol = data.groupby("Protocol").size().rename('NumOfPackets').reset_index()
   ptocol['Percentage']= ptocol["NumOfPackets"]/float(len(data))*100
   ptocol.sort_values(by=['Percentage'], ascending=[False], inplace=True)
   ptocol.to_csv(base+'_protocol_class_packets.csv', index = False)

   df=pd.read_csv(base+'_protocol_class_packets.csv', index_col='Protocol', usecols = ['Protocol','Percentage'])
   print df
   ax = df.plot(kind='bar', title ="Protocol Vs Percentage of total packets for "+base, grid=True)
   ax.set_xlim(right=10)
   ax.set_xlabel("Protocol")
   ax.set_ylabel("Percentage of the total packets")
   #plt.show()
   fig = ax.get_figure()
   fig.tight_layout()
   fig.savefig(base+'_proto_packets_bar.jpg')

   #ptocol.to_csv(base+'_protocol.csv', header = ["Protocol","NumOfPackets"])
   #df = pd.read_csv(base+'_protocol.csv')
   #print df
   #ax = ptocol.plot(kind='bar', title ="V comp",figsize=(15,10),legend=True, fontsize=12)
   #ax.set_xlabel("Protocol",fontsize=12)
   #ax.set_ylabel("Percentage",fontsize=12)

   #-----------------------------------------------
   #Protocol classification by length

   total_pkt_length = data["Length"].sum()
   print total_pkt_length
   ptocol_by_length = data.groupby("Protocol").Length.sum().rename('Accu_Pkt_Length').reset_index()
   ptocol_by_length['Percentage']= ptocol_by_length["Accu_Pkt_Length"]/float(total_pkt_length)*100
   ptocol_by_length.sort_values(by=['Accu_Pkt_Length'], ascending=[False], inplace=True)
   print ptocol_by_length
   ptocol_by_length.to_csv(base+'_protocol_class_length.csv', index = False)

   df=pd.read_csv(base+'_protocol_class_length.csv', index_col='Protocol', usecols = ['Protocol','Percentage'])
   print df
   ax = df.plot(kind='bar', title ="Protocol Vs Percentage of total bytes for "+base, grid=True)
   ax.set_xlim(right=10)
   ax.set_xlabel("Protocol")
   ax.set_ylabel("Percentage of the total bytes")
   #plt.show()
   fig = ax.get_figure()
   fig.tight_layout()
   fig.savefig(base+'_proto_length_bar.jpg')

   #------------------------------------------------
   # Calculating source destination pairs

   #  http://stackoverflow.com/questions/16031056/how-to-form-tuple-column-from-two-columns-in-pandas
   #data['src_dst_pair'] = data[['Source', 'Destination']].apply(tuple, axis=1) # for all traffic and udp traffic	
   data['src_dst_pair'] = data[['Source', 'Destination', 'SrcPort', 'DstPort']].apply(tuple, axis=1)	
   print data

   uniq_src_dst_pair = numpy.unique(data.src_dst_pair.ravel())	
   print uniq_src_dst_pair
   print len(uniq_src_dst_pair) 

   #  Sorting a dataframe based on pandas
   #  http://stackoverflow.com/questions/13636592/how-to-sort-a-pandas-dataframe-according-to-multiple-criteria 
   data.sort_values(by=['src_dst_pair','Time','Protocol'], ascending=[True,True,True], inplace=True)	
   print data
   data.to_csv(base+'_sorted.csv',mode = 'w', index=False)

   #  for each value in uniq_src_dst_pair, check it against data and print bytes. 
   #result = data.groupby(['Source','Destination']).Length.sum()    	
   #result = data.groupby(['Source','Destination']).Length.sum()    # for all traffic and udp traffic	
   result = data.groupby(['Source','Destination','SrcPort','DstPort']).Length.sum()    	
   print result 
   result.to_csv(base+'_flow_size.csv')

   df = pd.read_csv(base+'_sorted.csv', usecols = ['src_dst_pair', 'Info', 'Time', 'Length'])
   sorted_data= pd.read_csv(base+'_sorted.csv')
   #---------------------------------------------------------------------
   # Flow size Vs Flow duration for Src, Dest IP only 
   
   ip_level=sorted_data.groupby(['Source','Destination','SrcPort','DstPort']).agg({'Length': 'sum', 'Time': lambda x: x.max() - x.min()})
   ip_level.to_csv(base+'_ip_level.csv',index = False)

   iplevel = pd.read_csv(base+'_ip_level.csv')
   fig = plt.figure()
   plt.yscale('log')
   #plt.xscale('log')
   plt.title(' Size Vs Duration (at IP level) for '+base)
   plt.xticks(numpy.arange(min(iplevel['Time']), max(iplevel['Time'])+1, 20))
   plt.xlabel('Duration (in seconds)')
   plt.ylabel('Size (in bytes)')
   plt.scatter(iplevel['Time'], iplevel['Length'])
   fig.tight_layout()
   fig.savefig(base+'_iplevel_timevdur.png', dpi=fig.dpi)


   #---------------------------------------------------------------------
   # Used for computing the flow size Vs Duration for 5 tuple

   #resultef = df.groupby('src_dst_pair').apply(extract_flows)
   ##resultef.to_csv('output.csv', columns = ['src_dst_pair','Time','Length'])
   #resultef.sort_values(by=['Time'], ascending=[True], inplace=True)	
   #resultef.to_csv(base+'_output.csv')

   ##resultef.plot(x='Length', y='Time', style='o')
   #fig = plt.figure()
   #plt.yscale('log')
   #plt.xscale('log')
   #plt.title('Flow size Vs Flow Duration for '+base)
   ##http://stackoverflow.com/questions/12608788/changing-the-tick-frequency-on-x-or-y-axis-in-matplotlib
   ##plt.xticks(numpy.arange(min(resultef['Time']), max(resultef['Time'])+1, 10)) 
   #plt.xlabel('flow duration (in seconds)')
   #plt.ylabel('flow size (in bytes)')
   #plt.scatter(resultef['Time'], resultef['Length'])
   #fig.tight_layout()
   #fig.savefig(base+'_timevdur.png', dpi=fig.dpi)
   ##plt.show() # Depending on whether you use IPython or interactive mode, etc.
   ##print(resultef)

	
if __name__ == "__main__":
   main(sys.argv[1:])

# TCP packets

#group1_packets = data[(data.Protocol == "TCP") & (data.Source =="41.177.117.184") & (data.Destination =="41.177.3.224") ]
#print "# of GROUP1_PACKETS:  %d"% len(group1_packets)
##group1_packets.sort(['Length'], ascending=[True], inplace=True)
#print group1_packets
#group1_packets.to_csv('tcp_41_177.csv')
#
## TCP packets
#group3_packets = data[(data.Protocol == "TCP") & (data.Source =="244.3.160.239") & (data.Destination =="197.154.128.197") ]
#print "# of GROUP3_PACKETS:  %d"% len(group3_packets)
##group1_packets.sort(['Length'], ascending=[True], inplace=True)
#print group3_packets
#group3_packets.to_csv('tcp_group3.csv')
#
## UDP packets
#
#group2_packets = data[(data.Protocol == "UDP") & (data.Source =="41.177.161.164") & (data.Destination =="210.218.218.164") ]
#print "# of GROUP2_PACKETS:  %d"% len(group2_packets)
##group2_packets.sort(['Length'], ascending=[True], inplace=True)
#print group2_packets
#group2_packets.to_csv('udp_41_177.csv')
#
#print udp_packets

# List of IP Address



