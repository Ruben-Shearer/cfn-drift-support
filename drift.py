
import requests

from bs4 import BeautifulSoup

import boto3

import re

 

def write_file(filename, data):

    f = open(filename, "w")

    for line in data:

        f.write("%s\n" % line)

    f.close()

 

# Get all AWS CloudFormation resources

def get_all_aws_cfn_resources():

 

    all_aws_cfn_resources = []

 

    client = boto3.client('cloudformation')

 

    response = client.list_types(

        Visibility='PUBLIC',

        DeprecatedStatus='LIVE',

        Type='RESOURCE',

        Filters={

            'Category': 'AWS_TYPES'

        }

    )

 

    for type in response['TypeSummaries']:

        all_aws_cfn_resources.append(type['TypeName'])

 

    while "NextToken" in response:

        response = client.list_types(

            Visibility='PUBLIC',

            DeprecatedStatus='LIVE',

            Type='RESOURCE',

            Filters={

            'Category': 'AWS_TYPES'

            },

            NextToken=response["NextToken"]

        )

       

        for type in response['TypeSummaries']:

            all_aws_cfn_resources.append(type['TypeName'])

 

    # Ensure no duplicate resources

    all_aws_cfn_resources = set(all_aws_cfn_resources)

 

    # Check no empty entries

    while("" in all_aws_cfn_resources):

        all_aws_cfn_resources.remove("")

 

    print("## All CloudFormation Resources ##")

    print("Total: " + str(len(all_aws_cfn_resources)))

 

#    for resource in all_aws_cfn_resources:

#        print(resource)

 

    write_file("all_aws_cfn_resources.txt", all_aws_cfn_resources)

 

    return all_aws_cfn_resources

 

def get_table_data(url):

 

    headers = {

        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

    }

   

    # Fetch the content from the url

    response = requests.get(url, headers=headers, allow_redirects=True)

   

    if response.status_code != 200:

        raise Exception(f"Failed to load page {url}")

    # Parse the content with BeautifulSoup

    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the first table in the HTML (you can refine the search as needed)

    table = soup.find('table', id='w1404aac15c29c17')

   

    if table is None:

        raise Exception("No table found on the page")

    # Extract table headers

    headers = []

    for th in table.find_all('th'):

        headers.append(th.text.strip())

    # Extract table rows

    rows = []

    for tr in table.find_all('tr')[2:]: # Skip the header row

        cells = []

        for td in tr.find_all('td'):

            cells.append(td.text.strip())

        rows.append(cells)

    return headers, rows

 

# Scrape AWS CloudFormation resources that support drift

def scrape_drift_resources():

 

    drift_resources = []

 

    # Example usage

    url = "https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html"

    headers, rows = get_table_data(url)

   

    # Print the headers and rows

    #print("Headers:", headers)

 

    test_string = "test_string"

 

    for row in rows:

        if type(test_string) == type(row[0]):

            pattern = r'([a-zA-Z0-9]+)::([a-zA-Z0-9]+)::([a-zA-Z0-9]+)'

            match = re.search(pattern,row[0])

            if row[2] == 'Yes' and match:

                drift_resources.append(row[0])

 

    drift_resources = set(drift_resources)

 

    while("" in drift_resources):

        drift_resources.remove("")

 

    return drift_resources

 

def check_drift_resources_pesent_in_all_resources(drift_resources, all_aws_cfn_resources):

    found=0

    missing=0

    missing_resources=[]

    for resource in drift_resources:

        if resource in all_aws_cfn_resources:

            found = found + 1

        else:

            missing = missing + 1

            missing_resources.append(resource)

   

#    print(found)

#    print(missing)

#    print(missing_resources)

 

    for resource in missing_resources:

        if resource in drift_resources:

            drift_resources.remove(resource)

 

    return drift_resources

 

def get_drift_resources(all_aws_cfn_resources):

    get_drift_resources = []

 

    drift_resources = scrape_drift_resources()

 

    drift_resources = check_drift_resources_pesent_in_all_resources(drift_resources, all_aws_cfn_resources)

 

    print("# Drift Detection Supported Resources #")

    print("Total: " + str(len(drift_resources)))

 

    write_file("drift_resources.txt", drift_resources)

 

#    for resource in drift_resources:

#        print(resource)   

    

    return drift_resources

 

def get_non_drift_resources(drift_resources, all_aws_cfn_resources):

 

    non_drift_resources = all_aws_cfn_resources.copy()

 

    found = 0

    missing = 0

 

    for resource in all_aws_cfn_resources:

        if resource in drift_resources:

            non_drift_resources.remove(resource)

            found = found + 1

        else:

            missing = missing + 1

 

#    print(found)

#    print(missing)

 

    print("# Resources Which Don't Support Drift Detection #")

    print("Total: " + str(len(non_drift_resources)))

 

    write_file("non_drift_resources.txt", non_drift_resources)

 

#    for resource in non_drift_resources:

#        print(resource)

 

    return set(non_drift_resources)

 

try:

    # Get all CFN resources

    all_aws_cfn_resources = get_all_aws_cfn_resources()   

 

    # Get all CFN resources that support drift

    drift_resources = get_drift_resources(all_aws_cfn_resources)

   

    # Get CFN resource that don't support drift

    non_drift_resources = get_non_drift_resources(drift_resources, all_aws_cfn_resources)

 

except Exception as e:

    print(f'caught {type(e)}: e')

