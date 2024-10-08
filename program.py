import os
import sys
import csv
import re
import mt940
import pprint
import sys


#TODO add comments

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
documentNumber = "Brak zglosic"



#with open('e_dokum.txt', mode='w', newline='', encoding='windows-1250') as file:
with open('e_dokum.txt', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file,delimiter=';', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)


    for i, transaction in enumerate(transactions):
            pprint.pprint(transaction.data)        
            
            MA_account = "135"
            WN_account = "202"

            # Pełna data wyciągu
            fileData = transaction.data.get('date')
            # fileData.strftime('%Y-%m-%d')

            
            # Numer wyciągu
            statement_number = str(transactions.data['statement_number'])
            sequence_number = str(transactions.data['sequence_number'])      
            statement_number_list = list(statement_number)
            
            if(statement_number_list[0] == "0"):
                statement_number_elements = statement_number_list[1:]
                statement_number = ''.join(statement_number_elements)
            else:
                 statement_number = statement_number


            statement_number_sequence = str(statement_number + '/' + fileData.strftime('%Y'))
            full_statement_number_sequence = statement_number_sequence
            full_statement_number_sequence_description = "WBP" + statement_number_sequence

            # Liczba porządkowa
            ordinalNumber = i + 1
            
            # Faktury, nazwa firmy
            transactionDetails = transaction.data.get('transaction_details', '')


            isProwizjeAut = re.search(r"PROWIZJE AUT.", transactionDetails, re.DOTALL) if transactionDetails else None
            isPrzelewObciazenieVat = re.search(r"00PRZELEW PODZIELONY OBCIĄŻEN.*?", transactionDetails, re.DOTALL) if transactionDetails else None

            
            # notExtractedInvoiceNumber = re.search(r"<21INV/(?P<Ivalue>.*?)\/TXT", transactionDetails, re.DOTALL) if transactionDetails else None
            notExtractedInvoiceNumber = re.search(r"<20(?P<Ivalue>.*?)<30", transactionDetails, re.DOTALL) if transactionDetails else None
            invoiceNumber = notExtractedInvoiceNumber.group('Ivalue') if notExtractedInvoiceNumber else ''

            # NIP
            notExtractedTaxID = re.search(r"/IDC/(?P<Tvalue>.*?)<21(?:INV|/INV)", transactionDetails, re.DOTALL) if transactionDetails else None
            TaxID = notExtractedTaxID.group('Tvalue') if notExtractedTaxID else ''                   
            
            
            # Faktury wraz z przejściami do następnej linii
            descriptionFirstPartNotExtracted = re.search(r"<20(?P<DFPvalue>.*?)<30", transactionDetails, re.DOTALL) if transactionDetails else None
            descriptionFirstPart = descriptionFirstPartNotExtracted.group('DFPvalue') if descriptionFirstPartNotExtracted else ''

            # Nazwa firmy z przejściami do następnej linii
            notExtractedDescription  = re.search(r"<32(?P<Dvalue>.*?)<38", transactionDetails, re.DOTALL) if transactionDetails else None
            companyName = notExtractedDescription.group('Dvalue') if notExtractedDescription else ''
            # Usuń oznaczenia następnej linii
            companyName = re.sub(r"<3[3-7]", '', companyName)
       

            if(TaxID):
                # documentNumber = invoiceNumber + " NIP " + TaxID
                invoiceNumberMatch = re.search(r"/TXT(?P<Fvalue>.*?)<30", transactionDetails, re.DOTALL)

    
                # Wyodrębnienie dopasowanej wartości z grupy
                invoiceNumberRaw = invoiceNumberMatch.group('Fvalue') if invoiceNumberMatch else ''       

                invoiceNumberRaw = re.sub(r"/TXT", '', invoiceNumberRaw)
                invoiceNumberRaw = re.sub(r"<2[0-7]", '', invoiceNumberRaw)

                description = invoiceNumberRaw + " " + TaxID + " " + companyName
                pass
            else:
                invoiceNumberRaw = invoiceNumber
                invoiceNumber = re.sub(r"<2[0-7]", '', invoiceNumber)
                description = invoiceNumber + " " + companyName

            # description = re.sub(r'\s+', ' ', description).strip()
            
            # Kwota z jednostką
            amountwithUnit = str(transaction.data.get('amount'))
            # amount = re.search(r"[0-9]+.?[0-9]+", amountwithUnit) if amountwithUnit else None
            amount = re.search(r"\b\d+(?:\.\d+)?\b", amountwithUnit) if amountwithUnit else None

            is_amount_negative = bool(re.search(r"-", amountwithUnit)) if amountwithUnit else False     
            
            amount = amount.group()
            amount = float(amount)


            #ProwizjeAut
            if(isProwizjeAut):
                documentNumber = "PROWIZJE AUT."
                MA_account = "135"
                WN_account = "408-1"
                
            else:
                documentNumber = companyName

            #ObciazenieVat
            if(isPrzelewObciazenieVat):
                documentNumber = "OBCIĄŻENIE VAT"
                MA_account = "144"
                WN_account = "135"
            else:
                documentNumber = companyName

            if(amountwithUnit and is_amount_negative):
                 Temp_account =  MA_account
                 MA_account = WN_account
                 WN_account = Temp_account
                 
            isProwizjeAut = False
            isPrzelewObciazenieVat = False

            if(header):
                writer.writerow(["DOK", "WBP", 0,full_statement_number_sequence, full_statement_number_sequence_description,fileData,fileData,fileData,0.00,0,0,"","",0.00,0.00,"","","WBP"])
                header = False

            documentNumber = documentNumber.replace('\n', '').replace('\r', '')
            description = description.replace('\n', '').replace('\r', '')
            # documentNumber = ' '.join(documentNumber.split()).replace('\n', '').replace('\r', '').replace('\t', '')
            # description = ' '.join(description.split()).replace('\n', '').replace('\r', '').replace('\t', '')



            writer.writerow(["ZAP", 'WN',amount,WN_account,documentNumber,0,description,0])            
            writer.writerow(["ZAK", "MA",amount,MA_account,documentNumber,0,description,0])



remove_quotes_from_dates('e_dokum.txt')
