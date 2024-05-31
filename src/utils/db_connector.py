from pymongo import MongoClient

# Define the connection URI and database name here
CONNECTION_URI = "mongodb://localhost:27017"
DATABASE_NAME = "Marks"

def get_database():
    client = MongoClient(CONNECTION_URI)
    return client[DATABASE_NAME]

def merge_semester_collections(semesters, master_collection):
    db = get_database()
    """ Merge multiple semester collections into 'all_in_one'. """
    # Create the initial pipeline with the first semester collection
    initial_collection = semesters[0]
    pipeline = []

    # Append union stages for each subsequent semester collection
    for semester in semesters[1:]:
        pipeline.append({
            '$unionWith': {
                'coll': semester,
                'pipeline': [
                    {'$project': {'_id': 0, 'Name': 1, 'USN': 1, 'results': 1, 'Semester': 1}}
                ]
            }
        })

    # Group documents by USN, and aggregate semesters and results
    pipeline.extend([
        {
            '$group': {
                '_id': '$USN',
                'Name': {'$first': '$Name'},
                'allSem': {
                    '$push': {
                        'Semester': '$Semester',
                        'results': '$results'
                    }
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'USN': '$_id',
                'Name': 1,
                'allSem': 1
            }
        }
    ])

    # Perform the aggregation starting from the first semester collection
    results = db[initial_collection].aggregate(pipeline)

    # Insert aggregated results into 'allinone', first clearing existing data
    if master_collection in db.list_collection_names():
        db[master_collection].delete_many({})  # Optionally clear 'allinone' before inserting

    db[master_collection].insert_many(results)
