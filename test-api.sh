#!/bin/bash

# curl -s -w "\n\n%{time_connect} + %{time_starttransfer} = %{time_total}\n\n" https://naver.com
# curl -s -w "\n%{time_starttransfer}\n" https://naver.com
# curl -s -w "\n%{time_starttransfer}\n" -X GET "http://pri-api.dev.srch.skplanetx.com/api/ocb/1.0/search/all52?call_id=swagger_test&client_code=swagger_test&client_version=swagger_test&do_spell_checker=true&gugun_cd=001&ip_gugun_cd=001&ip_local_cd=50&local_cd=50&q=커피"
# curl -s -w "\n%{time_starttransfer}\n" -X GET "http://localhost:8080/api/ocb/1.0/search/all52?q=%EC%BB%A4%ED%94%BC&call_id=search_infra&client_code=client_code&client_version=test&n=50&do_spell_checker=true&lat=37.4021182&lon=127.1029423"

# ocb
curl -s -X GET "http://pri-api.dev.srch.skplanetx.com/api/ocb/2.0/search/all52?call_id=swagger_test&client_code=swagger_test&client_version=swagger_test&do_spell_checker=true&gugun_cd=001&ip_gugun_cd=001&ip_local_cd=50&local_cd=50&q=%EC%BB%A4%ED%94%BC&sort=benefit" -H "accept: */*" >> out-ocb1
curl -s -X GET "http://pri-api.dev.srch.skplanetx.com/api/ocb/2.0/search/all52?call_id=swagger_test&client_code=swagger_test&client_version=swagger_test&do_spell_checker=true&gugun_cd=001&ip_gugun_cd=001&ip_local_cd=50&local_cd=50&q=%EB%B2%84%EA%B1%B0%ED%82%B9&sort=benefit" -H "accept: */*" >> out-ocb2

# ocb.com
#curl -X GET "http://pri-api.dev.srch.skplanetx.com/api/ocb/1.0/search?call_id=swagger_test&client_code=swagger_test&client_version=swagger_test&do_spell_checker=true&gugun_cd=001&ip_gugun_cd=001&ip_local_cd=50&local_cd=50&q=%EC%BB%A4%ED%94%BC&sort=benefit" -H "accept: */*" >> out-ocbcom1

#curl -X GET "http://localhost:8080/api/ocb/1.0/search?call_id=swagger_test&client_code=swagger_test&client_version=swagger_test&do_spell_checker=true&gugun_cd=001&ip_gugun_cd=001&ip_local_cd=50&local_cd=50&q=%EC%BB%A4%ED%94%BC&sort=benefit" -H "accept: */*" >> out-ocbcom1n
