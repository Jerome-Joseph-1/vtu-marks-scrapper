import json 
from db_connector import get_database

db = get_database('Marks')

def add_credits():
    credits = json.load(open('../data/credits.json', 'r'))

    if 'credits' in db.list_collection_names():
        db['credits'].delete_many({})  # Optionally clear 'allinone' before inserting

    for key in credits.keys():
        for val in credits[key]:
            subject_code = list(val.keys())[0]
            credit_point = val[subject_code]
            db['credits'].insert_one({
                "subject_code": subject_code,
                "Semester": key.split()[1],
                "credit_point": credit_point
            })


def append_credits():
    import re

    all_in_one_collection = db['all_in_one']
    credits_collection = db['credits']

    credit_rules = list(credits_collection.find())

    for document in all_in_one_collection.find():
        # Apply each credit rule to the document
        for credit_rule in credit_rules:
            # Create a regex pattern from the subject_code in the credit rule
            pattern = credit_rule['subject_code']
            regex = re.compile(pattern)

            # Check each semester and subject in the document
            for semester in document['allSem']:
                if str(semester['Semester']) == str(credit_rule['Semester']):
                    for result in semester['results']:
                        if regex.match(result['Subject Code']):
                            result['Credit Points'] = credit_rule['credit_point']

        # Update the document in the database with the new information
        all_in_one_collection.update_one({'_id': document['_id']}, {'$set': {'allSem': document['allSem']}})

    print("Documents updated successfully.")
