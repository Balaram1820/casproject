from flask import Flask, render_template, request, jsonify, send_file
import json
import mysql.connector
from datetime import datetime

from function import (
    extract_text_from_pdf,
    fetch_data_from_text,
    extract_tables_from_pdf,
    convert_table_data_to_key_value_format,
    save_table_data_as_json,
    save_table_data_as_text,
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_pdf', methods=['POST'])
def process_pdf():
    pdf_file = request.files['pdf_file']
    pdf_password = request.form['pdf_password']

    pdf_file_path = 'uploaded_pdf.pdf'
    pdf_file.save(pdf_file_path)

    extracted_text = extract_text_from_pdf(pdf_file_path, pdf_password)
    data = fetch_data_from_text(extracted_text)

    output_json_file_path = 'data.json'
    with open(output_json_file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

    return jsonify({'message': 'Data extracted and saved successfully!', 'file_path': output_json_file_path})

@app.route('/process_tables', methods=['POST'])
def process_tables():
    pdf_file = request.files['pdf_file']
    pdf_password = request.form['pdf_password']

    pdf_file_path = 'uploaded_pdf.pdf'
    pdf_file.save(pdf_file_path)

    table_data = extract_tables_from_pdf(pdf_file_path, pdf_password)
    key_value_data = convert_table_data_to_key_value_format(table_data)

    json_output_file_path = 'table_data.json'
    save_table_data_as_json(key_value_data, json_output_file_path)

    txt_output_file_path = 'table_data.txt'
    save_table_data_as_text(key_value_data, txt_output_file_path)

    return jsonify({'message': 'Table data extracted and saved successfully!', 'json_file_path': json_output_file_path, 'txt_file_path': txt_output_file_path})



@app.route('/save_equities_data', methods=['POST'])
def save_equities_data():
    pdf_file = request.files['pdf_file']
    pdf_password = request.form['pdf_password']

    pdf_file_path = 'uploaded_pdf.pdf'
    pdf_file.save(pdf_file_path)

    table_data = extract_tables_from_pdf(pdf_file_path, pdf_password)
    key_value_data = convert_table_data_to_key_value_format(table_data)

    json_output_file_path = 'table_data.json'
    save_table_data_as_json(key_value_data, json_output_file_path)

    txt_output_file_path = 'table_data.txt'
    save_table_data_as_text(key_value_data, txt_output_file_path)

    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='master_user_details'
    )
    cursor = connection.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS equities (
            ISIN VARCHAR(255),
            SECURITY VARCHAR(255),
            CURRENT_BAL VARCHAR(255),
            FREE_BAL VARCHAR(255),
            LENT_BAL VARCHAR(255),
            SAFEKEEP_BAL VARCHAR(255),
            LOCKED_IN_BAL VARCHAR(255),
            PLEDGE_SETUP_BAL VARCHAR(255),
            PLEDGED_BAL VARCHAR(255),
            EARMARKED_BAL VARCHAR(255),
            PLEDGEE_BAL VARCHAR(255),
            MARKET_PRICE VARCHAR(255),
            VALUE VARCHAR(255)
        )
    '''
    cursor.execute(create_table_query)

    for row in key_value_data['Equities (E)']:
        isin = row.get("ISIN")
        security = row.get("SECURITY")
        current_bal = row.get("Current Bal.Free Bal.Lent Bal.")
        free_bal = row.get("Safekeep Bal.Locked In Bal.Pledge Setup Bal.")
        market_price = row.get("Market Price/ Face Valuein `")
        value = row.get("Valuein `")

        if isin == "ISIN" and security == "SECURITY" and current_bal == "Current Bal.Free Bal.Lent Bal." and free_bal == "Safekeep Bal.Locked In Bal.Pledge Setup Bal." and market_price == "Market Price/ Face Valuein `" and value == "Valuein `":
            continue

        insert_query = '''
            INSERT INTO equities (
                ISIN, SECURITY, CURRENT_BAL, FREE_BAL, LENT_BAL, SAFEKEEP_BAL, LOCKED_IN_BAL,
                PLEDGE_SETUP_BAL, PLEDGED_BAL, EARMARKED_BAL, PLEDGEE_BAL, MARKET_PRICE, VALUE
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            isin, security, current_bal, free_bal, '', '', '',
            '', '', '', '', market_price, value
        )
        cursor.execute(insert_query, values)

    connection.commit()
    connection.close()

    return jsonify({'message': 'Equities data saved to MySQL table!', 'json_file_path': json_output_file_path, 'txt_file_path': txt_output_file_path})

@app.route('/save_mutual_fund_folios', methods=['POST'])
def save_mutual_fund_folios():
    pdf_file = request.files['pdf_file']
    pdf_password = request.form['pdf_password']

    pdf_file_path = 'uploaded_pdf.pdf'
    pdf_file.save(pdf_file_path)

    table_data = extract_tables_from_pdf(pdf_file_path, pdf_password)
    key_value_data = convert_table_data_to_key_value_format(table_data)

    json_output_file_path = 'table_data.json'
    save_table_data_as_json(key_value_data, json_output_file_path)

    txt_output_file_path = 'table_data.txt'
    save_table_data_as_text(key_value_data, txt_output_file_path)

    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='master_user_details'
    )
    cursor = connection.cursor()

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS mutual_fund_folios (
            ISINUCC VARCHAR(255),
            ISIN_Description VARCHAR(255),
            Folio_No VARCHAR(255),
            No_of_Units VARCHAR(255),
            AverageCost_Per_Units VARCHAR(255),
            Total_Cost VARCHAR(255),
            Current_NAV_per_unit_in VARCHAR(255),
            Current_Value_in VARCHAR(255),
            UnrealisedProfit_Loss VARCHAR(255),
            AnnualisedReturn VARCHAR(255)
        )
    '''
    cursor.execute(create_table_query)

    for row in key_value_data['Mutual Fund Folios (F)']:
        ISINUCC = row.get("ISINUCC")
        ISIN_Description = row.get("ISIN Description")
        Folio_No = row.get("Folio No.")
        No_of_Units = row.get("No. ofUnits")
        AverageCost_Per_Units = row.get("AverageCost Per Units`")
        Total_Cost = row.get("Total Cost`")
        Current_NAV_per_unit_in = row.get("Current NAVper unitin `")
        Current_Value_in = row.get("Current Valuein `")
        UnrealisedProfit_Loss = row.get("UnrealisedProfit/(Loss)`")
        AnnualisedReturn = row.get("AnnualisedReturn(%)")

        if ISINUCC == "ISINUCC" and ISIN_Description == "ISIN Description" and Folio_No == "Folio No." and No_of_Units == "No. ofUnits" and AverageCost_Per_Units == "AverageCost Per Units`" and Total_Cost == "Total Cost`" and Current_NAV_per_unit_in == "Current NAVper unitin `" and Current_Value_in == "Current Valuein `" and UnrealisedProfit_Loss == "UnrealisedProfit/(Loss)`" and AnnualisedReturn == "AnnualisedReturn(%)":
            continue

        insert_query = '''
            INSERT INTO mutual_fund_folios (
                ISINUCC, ISIN_Description, Folio_No, No_of_Units, AverageCost_Per_Units,
                Total_Cost, Current_NAV_per_unit_in, Current_Value_in, UnrealisedProfit_Loss,
                AnnualisedReturn
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        values = (
            ISINUCC, ISIN_Description, Folio_No, No_of_Units, AverageCost_Per_Units,
            Total_Cost, Current_NAV_per_unit_in, Current_Value_in, UnrealisedProfit_Loss,
            AnnualisedReturn
        )
        cursor.execute(insert_query, values)

    connection.commit()
    connection.close()

    return jsonify({'message': 'Mutual Fund Folios data saved to MySQL table!', 'json_file_path': json_output_file_path, 'txt_file_path': txt_output_file_path})

@app.route('/download_file')
def download_file():
    file_path = request.args.get('file_path')
    return send_file(file_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
