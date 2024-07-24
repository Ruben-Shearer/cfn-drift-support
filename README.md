# cfn-drift-support

The CloudFormation [ListTypes](https://docs.aws.amazon.com/AWSCloudFormation/latest/APIReference/API_ListTypes.html) API can list all CloudFormation resources and the public [Resource type support](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/resource-import-supported-resources.html) CloudFormation document provides a list of resources which support drift however a comprehensive list of resources that don't support drift isn't currently available.

Using a Python script the public document can be scraped using the BeautifulSoup module and using some comparison logic a list of all CloudFormation resources, all resources which support drift and those which don't support drift can be generated. Please see the script.py file for a script to obtain these lists.
