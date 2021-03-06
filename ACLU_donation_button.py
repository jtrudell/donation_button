import mechanize
import botocore
import boto3
import os

# Adds default AWS region from an unmerged PR
try:
    sns     = boto3.client('sns')
    decrypt = boto3.client('kms').decrypt
except botocore.exceptions.NoRegionError:
    aws_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

    sns     = boto3.client('sns', region_name=aws_region)
    decrypt = boto3.client('kms', region_name=aws_region).decrypt

# +13333333333
phone_number='PHONE_INCLUDING_COUNTRYCODE_AND_AREA_CODE'

from base64 import b64decode

# I couldn't get the AWS enviro variables to work without getting Python padding errors. YMMV.
CC_number           = decrypt(CiphertextBlob=b64decode(os.environ['CC_number']))['Plaintext']
CC_expiration_month = decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_month']))['Plaintext']
CC_expiration_year  = decrypt(CiphertextBlob=b64decode(os.environ['CC_expiration_year']))['Plaintext']
CC_CSC              = decrypt(CiphertextBlob=b64decode(os.environ['CC_CSC']))['Plaintext']
# CC_number           = '0'
# CC_expiration_month = '0'
# CC_expiration_year  = '0'
# CC_CSC              = '0'

br = mechanize.Browser(factory=mechanize.RobustFactory())

def lambda_handler(event, context):
    br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]
    br.open("https://action.aclu.org/donate-aclu")
    br.select_form(nr=3)

    br.form['submitted[donation][aclu_recurring]'] = 0
    br.form['submitted[donation][amount]'] = ["other"]
    br.form['submitted[donation][other_amount]'] = "1"

    br.form['submitted[donor_information][first_name]'] = "My Name"
    br.form['submitted[donor_information][last_name]'] = "My Other Name"
    br.form['submitted[donor_information][email]'] = "jtrudell@gmail.com"

    br.form['submitted[billing_information][address]'] = "MY_ADDRESS"
    br.form['submitted[billing_information][city]'] = "MY_CITY"
    br.form['submitted[billing_information][state]'] = ["23"]
    br.form['submitted[billing_information][zip]'] = "60304"
    br.form['submitted[billing_information][country]'] = ["840"]

    br.form['submitted[credit_card_information][card_number]'] = CC_number
    br.form['submitted[credit_card_information][expiration_date][card_expiration_month]'] = [CC_expiration_month]
    br.form['submitted[credit_card_information][expiration_date][card_expiration_year]'] = [CC_expiration_year]
    br.form['submitted[credit_card_information][card_cvv]'] = CC_CSC

    br.form['submitted[credit_card_information][fight_for_freedom][1]'] = 0
    br.form['submitted[credit_card_information][profile_may_we_share_your_info][1]'] = 0

    response = br.submit()
    if "Thank You" in response.read():
        message = '$5 donated to the ACLU!'
        sns.publish(PhoneNumber=phone_number, Message=message)
    else:
        message = 'Error: no donation occurred :('
        sns.publish(PhoneNumber=phone_number, Message=message)

