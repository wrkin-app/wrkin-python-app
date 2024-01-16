import requests

def otp_sender(otp,number):
    url = "https://www.fast2sms.com/dev/bulkV2"

    payload = f'variables_values={otp}&route=otp&numbers={number}'
    headers = {
        'authorization': "ypW6IlbQoi3sxH7RcwBPDSMemrZdXNzunK5hva80q1GEfCOL9kZ8aJjc2bdI1xQXWtfmezk9rGBgyOsi",
        'Content-Type': "application/x-www-form-urlencoded",
        'Cache-Control': "no-cache",
        }

    response = requests.request("POST", url, data=payload, headers=headers)
    return response.json