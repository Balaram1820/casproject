import PyPDF2

def extract_text_from_pdf(pdf_path, password):
    """
    Extracts text from a PDF file.

    Args:
        pdf_path (str): Path to the PDF file.
        password (str): Password to decrypt the PDF file (if encrypted).

    Returns:
        str: Extracted text from the PDF file, or None if extraction fails.
    """
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        if pdf_reader.is_encrypted:
            pdf_reader.decrypt(password)
        if not pdf_reader.is_encrypted or pdf_reader.decrypt(password) == 1:
            num_pages = len(pdf_reader.pages)
            extracted_text = ""
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                extracted_text += page.extract_text()
            return extracted_text
        else:
            print("Incorrect password.")
            return None


#########################################################################################
import json


def extract_portfolio_composition(text):
    fstring = 'PORTFOLIO COMPOSITION'
    pos1 = text.find(fstring)
    text = text[pos1 + len(fstring):]
    lines = text.strip().split('\n')
    notes_index = lines.index('Notes:')
    block = lines[:notes_index]  # Extract the lines until "Notes:"
    return block



def extract_user_details(text):
    nsdl_id_index = text.find("NSDL ID:")
    consolidated_index = text.find("YOUR CONSOLIDATED")

    user_details = text[nsdl_id_index:consolidated_index].strip().split('\n')
    return user_details


def extract_email_and_phone(text):
    email_start = text.find("REGISTERED EMAIL") + len("REGISTERED EMAIL")
    email_end = text.find("AADHAAR NUMBER", email_start)
    email = text[email_start:email_end].strip()

    mobile_start = text.find("REGISTERED MOBILE") + len("REGISTERED MOBILE")
    mobile_end = text.find("DEMAT ACCOUNT WITH", mobile_start)
    mobile = text[mobile_start:mobile_end].strip()

    pan_start = text.find("PAN") + len("PAN")
    pan_end = text.find(")", pan_start)
    pan = text[pan_start:pan_end].strip()

    return email, mobile, pan


def extract_account_details(text):
    start_index = text.find("ISINs / SchemesValue in ")
    end_index = text.find("Portfolio Value TrendMonthly")

    account_details = text[start_index:end_index].strip().split('\n')
    return account_details


def fetch_data_from_text(text):
    data = {}

    # Extract user details
    user_details = extract_user_details(text)
    data["user_details"] = user_details

    # Extract email, phone, and PAN
    email, phone, pan = extract_email_and_phone(text)
    data["email"] = email
    data["phone"] = phone
    data["pan"] = pan

    # Extract portfolio composition
    portfolio_composition = extract_portfolio_composition(text)
    data["portfolio_composition"] = portfolio_composition


    # Extract account details
    account_details = extract_account_details(text)
    data["account_details"] = account_details
  

    return data

###########################################################################
import pdfplumber
import json


def extract_tables_from_pdf(pdf_path, password):
    table_data = {}

    with pdfplumber.open(pdf_path, password=password) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()

            for i, table in enumerate(tables, start=1):
                if i == 4:
                    table_name = "Table_4"
                    if table_name not in table_data:
                        table_data[table_name] = []

                    is_equities_table = False
                    for row in table:
                        cleaned_row = [cell.replace('\n', '') if cell is not None else '' for cell in row]
                        table_data[table_name].append(cleaned_row)

                        if "Equities (E)" in cleaned_row:
                            is_equities_table = True

                    if is_equities_table:
                        equities_table_name = "Equities (E)"
                        if equities_table_name not in table_data:
                            table_data[equities_table_name] = []

                        start_equities = False
                        for row in table_data[table_name]:
                            if start_equities:
                                if "Equities (E)" in row:
                                    break
                                equities_row = [cell if cell != "Equities (E)" else "" for cell in row]
                                table_data[equities_table_name].append(equities_row)
                            elif "Equities (E)" in row:
                                start_equities = True

                        table_data[table_name] = [row for row in table_data[table_name] if "Equities (E)" not in row]

                elif i == 5:
                    table_name = "Table_5"
                    if table_name not in table_data:
                        table_data[table_name] = []

                    is_mutual_funds_table = False
                    for row in table:
                        cleaned_row = [cell.replace('\n', '') if cell is not None else '' for cell in row]
                        table_data[table_name].append(cleaned_row)

                        if "Mutual Fund Folios (F)" in cleaned_row:
                            is_mutual_funds_table = True

                    if is_mutual_funds_table:
                        mutual_funds_table_name = "Mutual Fund Folios (F)"
                        if mutual_funds_table_name not in table_data:
                            table_data[mutual_funds_table_name] = []

                        start_mutual_funds = False
                        for row in table_data[table_name]:
                            if start_mutual_funds:
                                if "Mutual Fund Folios (F)" in row:
                                    break
                                mutual_funds_row = [cell if cell != "Mutual Fund Folios (F)" else "" for cell in row]
                                table_data[mutual_funds_table_name].append(mutual_funds_row)
                            elif "Mutual Fund Folios (F)" in row:
                                start_mutual_funds = True

                        table_data[table_name] = [row for row in table_data[table_name] if "Mutual Fund Folios (F)" not in row]

    return table_data


def convert_table_data_to_key_value_format(table_data):
    key_value_data = {}
    for table_name, rows in table_data.items():
        key_value_data[table_name] = []
        for row in rows:
            key_value_data[table_name].append(dict(zip(rows[0], row)))
    return key_value_data


def save_table_data_as_json(table_data, output_file_path):
    with open(output_file_path, 'w') as json_file:
        json.dump(table_data, json_file, indent=4)


def save_table_data_as_text(table_data, output_file_path):
    with open(output_file_path, 'w') as txt_file:
        for table_name, rows in table_data.items():
            txt_file.write(f"{table_name}\n")
            for row in rows:
                txt_file.write(", ".join(f"{key}: {value}" for key, value in row.items()) + "\n")
            txt_file.write("\n")


# Main script
if __name__ == "__main__":
    pdf_path = 'final/NSDLe-CAS_104980391_APR_2023.PDF'
    password = 'AHPPP6410M'
    table_data = extract_tables_from_pdf(pdf_path, password)
    key_value_data = convert_table_data_to_key_value_format(table_data)

    json_output_file_path = 'table_data.json'
    save_table_data_as_json(key_value_data, json_output_file_path)

    txt_output_file_path = 'table_data.txt'
    save_table_data_as_text(key_value_data, txt_output_file_path)

#####################################################################################
