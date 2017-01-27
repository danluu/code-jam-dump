import csv
import json
import requests
import time

# connections = ['FIOS', 'Cable', '3G', 'Dial']
connections = ['FIOS', 'Dial']
urls = ['http://danluu.com', 'https://danluu.com']
num_runs = 2

key = ''
with open('key.txt') as f:
    key = f.readline().rstrip()

payload = {'url': 'http://danluu.com/',
           'k':key,
           'f':'json',  # return json results.
           'noheaders':'1',  # don't save headers
           'fvonly':'1',  # first view only
           'runs':num_runs,
           'noopt':'1'  # disable optimization checks???
}

def send_test_request(payload):    
    print('sending request')
    req = requests.get('http://www.webpagetest.org/runtest.php', params=payload)
    result = req.json()
    print(result)
    if result['statusText'] != 'Ok':
        print("send_test_request FAILED!!!!")
        raise Exception('test_request status not Ok')
    return result['data']['jsonUrl']

def poll_test_result(json_url):
    num_attempts = 0
    result = {}
    while True:
        print("Polling attempt {}".format(num_attempts))
        req_result = requests.get(json_url)
        num_attempts += 1
        if req_result.status_code == 200 or num_attempts > 100:
            result = req_result.json()
            print(req_result.json())
            if result['statusCode'] == 200:
                break
        time.sleep(5)

    result = req_result.json()
    return result

def save_result(result, url, connection):    
    successful_runs = result['data']['successfulFVRuns']
    bytes_in = result['data']['average']['firstView']['bytesIn']
    num_reqs = result['data']['average']['firstView']['requests']
    tt_complete = result['data']['average']['firstView']['visualComplete']

    print("successful_runs: {}".format(successful_runs))
    print("num_reqs: {}".format(num_reqs))
    print("tt_complete: {}".format(tt_complete))

def save_json_urls(payload, urls, connections):
    csvf = open('/tmp/wpt_urls.csv', 'w', newline='')
    writer = csv.writer(csvf)
    for uu in urls:
        for cc in connections:
            payload['location'] = "Dulles.{}".format(cc)
            payload['url'] = uu
            json_url = send_test_request(payload)
            writer.writerow(['url','connection','wpt_json'])
            writer.writerow([uu, cc, json_url])
            print("{},{},{}".format(uu, cc, json_url))
            # json_url = 'http://www.webpagetest.org/jsonResult.php?test=170127_BG_CF'
        
            #result = poll_test_result(json_url)
            # print_results(result, cc)

def get_test_results():
    csvf_urls = open('/tmp/wpt_urls.csv')
    reader = csv.reader(csvf_urls)
    header = next(reader)
    assert header == ['url','connection','wpt_json']

    # csvf_results = open('/tmp/wpt_results.csv', 'w', newline='')    
    # writer = csv.writer(csvf_results)
    
    per_url = {}

    for row in reader:
        failed = False
        url = row[0]
        connection = row[1]
        wpt_json = row[2]

        if not url in per_url:
            per_url[url] = {}

        result = poll_test_result(wpt_json)

        bytesIn = result['data']['average']['firstView']['bytesIn']
        connections = result['data']['average']['firstView']['connections']
        requests = result['data']['average']['firstView']['requests']
        if 'bytesIn' in per_url[url]:
            if bytesIn < per_url[url]['bytesIn']:
                failed = True
        else:
            per_url[url]['bytesIn'] = bytesIn

        per_url[url]['connections'] = connections

        if 'requests' in per_url[url]:
            if requests < per_url[url]['requests']:
                failed = True
        else:
            per_url[url]['requests'] = requests
                    
        save_result(result, url, connection)

    with open('/tmp/wpt_per_url.json','w') as jsonf:
        json.dump(per_url, jsonf)
        

# save_json_urls(payload, urls, connections)
get_test_results()
    
    
