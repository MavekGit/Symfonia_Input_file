import os
import sys
import csv
import re
import mt940
import pprint
import sys


def remove_quotes_from_dates(file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        

    content = re.sub(r'"(\d{4}-\d{2}-\d{2})"', r'\1', content)
    # print(content)
    with open(file_path, 'w', encoding='windows-1250') as file:
        file.write(content)



transactions = mt940.parse('dok.sta',encoding='windows-1250')
#transactions = mt940.parse('dok.sta')
header = True

MA_account = "135"
WN_account = "202"



#with open('e_dokum.txt', mode='w', newline='', encoding='windows-1250') as file:
with open('e_dokum.txt', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file,delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)


    for i, transaction in enumerate(transactions):
            #pprint.pprint(transaction.data)        
            
            fileData = transaction.data.get('date')
            # fileData.strftime('%Y-%m-%d')

            
            
            statement_number = str(transactions.data['statement_number'])
            sequence_number = str(transactions.data['sequence_number'])      
            statement_number_list = list(statement_number)
            
            if(statement_number_list[0] == "0"):
                statement_number_elements = statement_number_list[1:]
                statement_number = ''.join(statement_number_elements)
            else:
                 statement_number = statement_number

            statement_number_sequence = str(statement_number + '/' + fileData.strftime('%Y'))
            # BEZ WBP nagłówek bez pierwszego zera przykład 0045/2024
            full_statement_number_sequence = statement_number_sequence
            full_statement_number_sequence_description = "Wyciag bankowy nr " + statement_number_sequence

            ordinalNumber = i + 1
            
            transactionDetails = transaction.data.get('transaction_details', '')

            isProwizjeAut = re.search(r"PROWIZJE AUT.", transactionDetails, re.DOTALL) if transactionDetails else None

            if(isProwizjeAut):
                WN_account = "408-1"

            
            notExtractedInvoiceNumber = re.search(r"<21INV/(?P<Ivalue>.*?)\/TXT", transactionDetails, re.DOTALL) if transactionDetails else None

            notExtractedTaxID = re.search(r"/IDC/(?P<Tvalue>.*?)/<21INV/", transactionDetails, re.DOTALL) if transactionDetails else None

            invoiceNumber = notExtractedInvoiceNumber.group('Ivalue') if notExtractedInvoiceNumber else ''
            TaxID = notExtractedTaxID.group('Tvalue') if notExtractedTaxID else ''               
            
            if(invoiceNumber):
                documentNumber = invoiceNumber + " NIP " + TaxID
            else:
                 documentNumber = ''

            descriptionFirstPartNotExtracted = re.search(r"<20(?P<DFPvalue>.*?)<30", transactionDetails, re.DOTALL) if transactionDetails else None
            descriptionFirstPart = descriptionFirstPartNotExtracted.group('DFPvalue') if descriptionFirstPartNotExtracted else ''

            notExtractedDescription  = notExtractedTaxID = re.search(r"<32(?P<Dvalue>.*?)<38", transactionDetails, re.DOTALL) if transactionDetails else None
            description = notExtractedDescription.group('Dvalue') if notExtractedDescription else ''
            description = re.sub(r"<3[3-7]", '', description)

            description =  str(description) + " " + str(descriptionFirstPart)
            description = re.sub(r'\s+', ' ', description).strip()
            
            amountwithUnit = str(transaction.data.get('amount'))
            # amount = re.search(r"[0-9]+.?[0-9]+", amountwithUnit) if amountwithUnit else None
            amount = re.search(r"\b\d+(?:\.\d+)?\b", amountwithUnit) if amountwithUnit else None

            is_amount_negative = re.search(r"-", amountwithUnit) if amountwithUnit else None

            if(amountwithUnit and not is_amount_negative):
                 MA_account = "201"
                 WN_account = "135"
                 
            
            amount = amount.group()
            amount = float(amount)


            if(header):
                writer.writerow(["DOK", "WBP", 0,full_statement_number_sequence, full_statement_number_sequence_description,fileData,fileData,fileData,0.00,0,0,"","",0.00,0.00,"","","WBP"])
                header = False


            writer.writerow(["ZAP", 'WN',amount,WN_account,documentNumber,0,description,0])
            writer.writerow(["ZAK", "MA",amount,MA_account,documentNumber,0,description,0])

remove_quotes_from_dates('e_dokum.txt')
