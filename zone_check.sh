#!/bin/sh
#
#
#
ZONE_LIST=$1
OLD_DNS=$2
TS=`date "+%Y%m%d%H%M%S"`
HOSTNAME=`hostname`

if [ $# == 0 ]
then
echo "usage: $0 <zone-list-file> <DNS-server-IP>";
exit;
fi

mkdir -p zonefiles
for zone in `cat $ZONE_LIST`;
do
	echo "Checking zone $zone ..."
	ZONE_TMP="zone.axfr.$$"
	dig +noedns +norec @$OLD_DNS $zone axfr > $ZONE_TMP;
	SOA=`grep 'SOA' $ZONE_TMP | tail -1 | awk '{print $7;}'`
	/usr/local/nessy2/bin/named-checkzone -k ignore -i full -n warn $zone $ZONE_TMP >> zone_parse_$TS.log 2>&1;
	mv $ZONE_TMP zonefiles/$zone.$SOA;
done

tar -czvf /data1/exports/axfr_incoming_$HOSTNAME_$TS.tar.gz zone_parse_$TS.log zonefiles/

