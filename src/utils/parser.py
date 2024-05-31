import bs4

def parse_to_json(file_path):
    custom_colon_trimmer = lambda x: x.text.split(':')[-1].strip()
    result = {
        "Name": "",
        "USN": "",
        "Semester": "",
        "results": []
    }

    soup = bs4.BeautifulSoup(open(f'{file_path}', 'r'), 'html.parser')
    tables = soup.findAll('table')

    headerCells = tables[0].findAll('td')
    result["Name"] = custom_colon_trimmer(headerCells[3])
    result["USN"] = custom_colon_trimmer(headerCells[1])

    rows = soup.findAll('div', class_="row")
    details_div = rows[6].findAll('div')

    result["Semester"] = custom_colon_trimmer(details_div[1])
    
    results_divs = soup.findAll('div', class_="divTable")[0]
    subjects_rows = results_divs.findAll('div', class_ = "divTableRow")

    per_subject_details = {}
    titles = []

    for title in subjects_rows[0].findAll('div', class_="divTableCell"):
        per_subject_details[custom_colon_trimmer(title)] = ""
        titles.append(custom_colon_trimmer(title))

    for row in subjects_rows[1:]:
        index = 0
        for details in row.findAll('div', class_ = "divTableCell"):
            per_subject_details[titles[index]] = custom_colon_trimmer(details)
            index += 1
        result['results'].append(per_subject_details.copy())
    # pprint(result)
    
    return result

# def insert_to_db(folder, semester):
#     db = get_database()
#     for file in os.listdir(folder):
#         try:
#             result_document = parse_to_json(f'{folder}/{file}')
#         # print(result_document)
#         except Exception as e:
#             logger.error(e)

#         db[semester].insert_one(result_document)
#         break

# insert_to_db('../results', 'sem_vii')