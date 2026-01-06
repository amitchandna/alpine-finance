from shared_utils.connection_management import ConnectionManager
from ETL.data_transformation.cleaning_utils import Cleaner


def insert_cleaned_data(section):
    db = ConnectionManager()
    # Grab the data, Clean it then return it
    # TODO: Grab the data and edit in in place + return it to a new table
    db.connect_to_database()

    cl = Cleaner()
    for record in db.fetch_data(sql_template=f'''select id, ticker, filing_date,
                                                filing_url, {section} 
                                                from raw_ten_k_data''', batch_size=1):

        processed_data = cl.remove_item_markers(record[0][4])
        processed_data = cl.replace_empty_fields(processed_data)
        processed_data = cl.remove_table_strings(processed_data)
        processed_data = cl.to_lowercase(processed_data)
        db.insert_data(table_name=f"processed_ten_k_{section}", data={'id': record[0][0],
                                                                       'ticker': record[0][1],
                                                                       'filing_date': record[0][2],
                                                                       'filing_url': record[0][3],
                                                                       f"{section}": processed_data})



section_list = ['section_one',
                'section_one_a',
                'section_one_b',
                'section_two',
                'section_three',
                'section_four',
                'section_five',
                'section_six',
                'section_seven',
                'section_seven_a',
                'section_eight',
                'section_nine',
                'section_nine_a',
                'section_nine_b',
                'section_ten',
                'section_eleven',
                'section_twelve',
                'section_thirteen',
                'section_fourteen',
                'section_fifteen']

for i in section_list:
    insert_cleaned_data(section=i)
