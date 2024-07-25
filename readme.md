# VTU Result Scraper ( 2018 Scheme )

The VTU Result Scraper is a Python application designed to automate the fetching of exam results from the VTU (Visvesvaraya Technological University) official results website. This project utilizes various modules to handle tasks such as web scraping, image processing for CAPTCHA recognition, and database operations.

## Features

- Fetching results using USN range.
- CAPTCHA decoding using OCR.
- Saving results locally and inserting them into a MongoDB database.
- Handling retries for failed downloads.
- Merging data from multiple semesters into a single database collection.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.6 or higher
- Pip for Python 3
- MongoDB server running on the default port (27017)

## Setup

Clone the repository to your local machine:
```bash
git clone git@github.com:Jerome-Joseph-1/vtu-marks-scrapper.git
cd vtu-result-scraper
```

Install the required Python libraries:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the root directory with the necessary API keys and database credentials:
```plaintext
API_KEY=your_ocr_api_key
```

## Usage

The script can be executed with various commands depending on the intended operation:
```bash
# Fetch results and save them to a specified folder
python3 scrapper.py fetch --folder semester6 --sem 6 --start 1

# Insert results into a MongoDB database from a specified folder
python3 scrapper.py insert --folder semester6 --collection semester6
```

### Commands and Options
- `fetch`: Fetch results from the VTU website.
- `fetch_one` : Fetch individual result from the VTU website
- `insert`: Insert results into a database.
- `manual`: Manually fetch results for specific USNs.
- `merge`: Merge results from multiple semesters.
- `--folder`: Specify the folder for downloading or reading results.
- `--sem`: Specify the semester code.
- `--start`: Specify the starting USN number.
- `--collection`: Specify the MongoDB collection name.

## Contributing

Contributions to this project are welcome. To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.
