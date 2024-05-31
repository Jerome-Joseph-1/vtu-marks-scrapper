import argparse
import requests, bs4 
import json
from modules.imageProcessor import ImageProcessor
from utils.logger import create_logger 
import os 
from utils.db_connector import get_database, merge_semester_collections
from utils.parser import parse_to_json
from dotenv import load_dotenv

load_dotenv()

requests.packages.urllib3.disable_warnings()

vtu_exam_codes = {
    "2": "JAEcbcs",
    "3": "FMEcbcs22",
    "4": "JJEcbcs22",
    "5": "JFEcbcs23",
    "6": "JJEcbcs23",
    "7": "DJcbcs24",
    "8": "JJEcbcs24"
}

VTU_DOMAIN = 'https://results.vtu.ac.in'
VTU_SEM_CODE = None
VTU_MARKS_ENDPOINT = None
VTU_RESULTS = None
OCR_URL = "https://api.ocr.space/parse/image"

imageProcessor = ImageProcessor()
logger = create_logger()

failed_numbers = []

get_usn = lambda x: '4SO20CS' + str(x).rjust(3, '0')

def generate_new_token():
    response = requests.get(f'{VTU_DOMAIN}/{VTU_MARKS_ENDPOINT}', verify=False)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    cookie = {'VISRE': response.cookies.get('VISRE')}
    token = soup.findAll('input', {'name': 'Token'})[0].attrs['value']

    return (cookie, token, soup)

def get_captcha_code(cookie, soup, usn):
    logger.info("Downloading Captcha")
    captchaEndpoint = soup.findAll('img', {'alt': 'CAPTCHA code'})[0].attrs['src']
    response = requests.get(f'{VTU_DOMAIN}{captchaEndpoint}', verify=False, cookies=cookie)

    with open(f'{usn}.png', 'wb') as f:
        f.write(response.content)
    # import time
    # time.sleep(3)
    image_path = imageProcessor.sanitize(f'{usn}.png')

    data = {'apikey': os.getenv('API_KEY')}
    files = {'file': (image_path, open(image_path, 'rb'))}

    logger.info("Decoding Captcha")
    captchaCodeResponse = requests.post(OCR_URL, files=files, data=data)
    captchaResults = json.loads(captchaCodeResponse.text)
    os.remove(image_path)

    logger.info(f"Got Captcha Results with status Code: {captchaCodeResponse.status_code}")
    captchaCode = captchaResults['ParsedResults'][0]['ParsedText'].split('\r\n')[0]
    
    return captchaCode


def init_connection(number):
    usn = get_usn(number)
    cookie, token, soup = generate_new_token()
    captchaCode = get_captcha_code(cookie, soup, usn)

    return (cookie, token, captchaCode)

def construct_payload(usn, token, captchaCode):
    return {
        'Token': str(token),
        'lns': str(usn),
        'captchacode': str(captchaCode)
    }

def download_result(number, token, cookie, captchaCode):
    payload = construct_payload(get_usn(number), token, captchaCode)
    response = requests.post(f"{VTU_DOMAIN}/{VTU_RESULTS}", cookies=cookie, data=payload, verify=False)
    return response 

# TODO: Modify logic of manual_push
# Temporary fix 
def manual_push(folder="results"):
    manualNumber = []
    response = None
    
    attempt = 0
    number = manualNumber[0]
    while response == None or not (response.status_code == 200 and get_usn(number) in response.text):
        print("Attempt: ", attempt)
        cookie, token, captchaCode = init_connection(number)
        response = download_result(number, token, cookie, captchaCode)
        logger.info(f"Captcha Code: {captchaCode}")
        attempt += 1

    for number in manualNumber:
        logger.info(f"Trying to Download results of : {get_usn(number)}")
        
        response = download_result(number, token, cookie, captchaCode)
        if response.status_code == 200 and get_usn(number) in response.text:
            logger.info("Download Successful")

            with open(f'{folder}/results_{get_usn(number)}.html', 'wb') as f:
                f.write(response.content)
        else:
            attempt = 0
            while response == None or not (response.status_code == 200 and get_usn(number) in response.text):
                print("Attempt: ", attempt)
                cookie, token, captchaCode = init_connection(number)
                response = download_result(number, token, cookie, captchaCode)
                logger.info(f"Captcha Code: {captchaCode}")
                attempt += 1
                
            logger.info("Download Successful")

            with open(f'{folder}/results_{get_usn(number)}.html', 'wb') as f:
                f.write(response.content)


def fetch_results(folder="results", number=1):
    cookie, token, captchaCode = init_connection(1)
    
    lastNumber, failureCount = 190, 0

    def get_next_number(number):
        skip_numbers = [10, 19, 47, 48, 70, 72, 77, 99, 167]
        while number + 1 in skip_numbers: 
            number += 1
        return (number + 1, 0)
    
    while number < lastNumber:
        logger.info(f"Trying to Download results of : {get_usn(number)}")
        response = download_result(number, token, cookie, captchaCode)

        if response.status_code == 200 and get_usn(number) in response.text:
            logger.info("Download Successful")

            with open(f'{folder}/results_{get_usn(number)}.html', 'wb') as f:
                f.write(response.content)
            number, failureCount = get_next_number(number)
            
        else:
            logger.error(f"Failed: Retrying with new Captcha ... Attempt {failureCount + 1}")
            cookie, token, captchaCode = init_connection(number)
            failureCount += 1
        
        if failureCount > 5:
            failed_numbers.append(number)
            logger.error(f"Failed: Skipping USN : {get_usn(number)}")
            number, failureCount = get_next_number(number)

def insert_to_db(folder="result", collection="dump"):
    db = get_database()

    for file in os.listdir(folder):
        result_document = parse_to_json(f'{folder}/{file}')

        try:
            db[collection].insert_one(result_document)
            logger.info(f"Inserted Document successfully [{result_document['USN']}]")
        except Exception as e:
            logger.error(f"Failed to insert Document [{result_document['USN']}]. Error : {e}")


def main(args):
    global VTU_SEM_CODE, VTU_MARKS_ENDPOINT, VTU_RESULTS
    VTU_SEM_CODE = vtu_exam_codes[args.sem]
    VTU_MARKS_ENDPOINT = f'{VTU_SEM_CODE}/index.php'
    VTU_RESULTS = f'{VTU_SEM_CODE}/resultpage.php'

    if args.action == 'fetch':
        if not os.path.exists(args.folder):
            os.makedirs(args.folder)
        fetch_results(folder=args.folder, number=int(args.start))
        logger.info(f"Failed to download results for : {', '.join(str(i) for i in failed_numbers)}" )
    elif args.action == 'insert':
        insert_to_db(folder=args.folder, collection=args.collection)
    elif args.action == 'manual':
        manual_push(args.folder)
    elif args.action == 'merge':
        if input("Make sure to add the semester collection names in the code.\nHave you added it ? (y/N)") == "y":
            merge_semester_collections(os.listdir('src/results_cs'), 'all_in_one')
            logger.info("Merged Successfully")
    else:
        logger.error("Invalid use-case")

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description="Manage result operations.")
    
    # Add arguments to the parser
    parser.add_argument('action', choices=['fetch', 'insert', 'exit', 'manual', 'merge'], help='Action to perform.')
    parser.add_argument('--folder', default='results', help='Folder to process (default: results)')
    parser.add_argument('--start', default=1, help='Starting Number (default: 1)')
    parser.add_argument('--sem', default="2", help='Semester (default: 2)')
    parser.add_argument('--collection', default='dump', help='Database collection to use (default: dump)')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Run the main function
    main(args)


"""
Usage:

python3 scrapper.py fetch --folder {folder_name} --sem {semester} --start {starting number}
python3 scrapper.py insert --folder {folder_name} --collection {collection_name}

"""