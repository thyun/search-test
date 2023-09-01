export BOOTSTRAP_SERVER=aaa,bbb,ccc
bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER --reset-offsets --topic ocb-comm-feeds --group ocb-comm-feed-group --command-config client.properties --to-datetime 2023-08-16T06:00:00.000 --execute
bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER --reset-offsets --topic ocb-comm-users --group ocb-comm-user-group --command-config client.properties --to-datetime 2023-08-16T06:00:00.000 --execute
bin/kafka-consumer-groups.sh --bootstrap-server $BOOTSTRAP_SERVER --reset-offsets --topic ocb-comm-tags --group ocb-comm-tag-group --command-config client.properties --to-datetime 2023-08-16T06:00:00.000 --execute

