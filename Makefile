upload:
	tar -cf client.tar client
	scp client.tar wcrichto@acmalgo.com:awap/server/www/
	rm client.tar