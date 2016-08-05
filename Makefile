all:
	make clean
	#python first.py -i first.csv

alltraffic:
	make clean
	python wports.py -i univ1_pt1_all_traffic.csv
tcp:
	make clean
	python wports.py -i univ1_pt1_tcp_traffic.csv
udp:
	make clean
	python wports.py -i univ1_pt1_udp_traffic.csv
others:
	make clean
	python wports.py -i univ1_pt1_other_traffic.csv

clean:
	rm -f first_*.*
	rm -f univ1_pt1_all_traffic_*.*
	rm -f univ1_pt1_tcp_traffic_*.*
	rm -f univ1_pt1_udp_traffic_*.*
	rm -f univ1_pt1_other_traffic_*.*
