#!/bin/bash
echo `date`
CODE=`curl -s -w "%{http_code}\n" -o /dev/null "http://pri-api.dev.srch.skplanetx.com/api/ocb/2.0/search/all52?q=%EC%BF%A0%ED%8F%B0"`
#CODE=`curl -s -w "%{http_code}\n" -o /dev/null "http://pri-admin.dev.srch.skplanetx.com"`
if [ "$CODE" == "200" ]
then
  echo "SUCCESS - http_code=$CODE"
else
  echo "FAIL - http_code=$CODE"
fi

#curl -s "http://pri-api.dev.srch.skplanetx.com/api/ocb/2.0/search/all52?q=%EC%BF%A0%ED%8F%B0"
