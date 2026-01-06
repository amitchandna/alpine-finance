import datetime
from jinja2 import Template
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, URL, insert, Table, MetaData, text
from sec_api import ExtractorApi, MappingApi, QueryApi
from concurrent.futures import ThreadPoolExecutor


class ConnectionManager:
    def __init__(self):
        self.engine = None
        self.connection = None
        load_dotenv()
        self.host = os.getenv("LOCAL_PG_HOST")
        self.port = os.getenv("LOCAL_PG_PORT")
        self.user = os.getenv("LOCAL_PG_USER")
        self.password = os.getenv("LOCAL_PG_PWD")
        self.database = os.getenv("LOCAL_DB_NAME")

    def connect_to_database(self):
        try:
            url_object = URL.create(
                drivername="postgresql",
                host=self.host,
                port=self.port,
                username=self.user,
                password=self.password,
                database=self.database,
                query=None,
            )
            engine = create_engine(url_object)
            connection = engine.connect()
            print(f"Successfully connected to the db")
            return connection
        except Exception as e:
            print(f"Failed to connect to the database; more info -> {e}")

    def insert_data(self, table_name: str, data: dict):
        """For updating data within the db"""
        try:
            conn = self.connect_to_database()
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=conn)
            insert_statement = insert(table).values(data)
            conn.execute(insert_statement)
            conn.commit()
            print(f"Successfully inserted the data into the database")
            self.disconnect()
        except Exception as e:
            print(f"Failed to load the data into the database; more info -> {e}")

    def insert_json_data(self, table_name: str, json_response: dict):
        try:
            conn = self.connect_to_database()
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=conn)

            if isinstance(json_response, list):
                for item in json_response:
                    # Remove 'id' from the dictionary and assign its value to 'sec_id'
                    item["sec_id"] = item.pop("id", None)
                    column_names = [
                        column.name for column in table.columns if column.name != "id"
                    ]
                    values_dict = {column: item.get(column) for column in column_names}
                    insert_statement = insert(table).values(**values_dict)
                    conn.execute(insert_statement)
            elif isinstance(json_response, dict):
                json_response["sec_id"] = json_response.pop("id", None)
                column_names = [
                    column.name for column in table.columns if column.name != "id"
                ]
                values_dict = {
                    column: json_response.get(column) for column in column_names
                }
                insert_statement = insert(table).values(**values_dict)
                conn.execute(insert_statement)

            conn.commit()
            self.disconnect()
        except Exception as e:
            print(f"Failed to load the json data into the database; more info -> {e}")

    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
                print("Database connection closed successfully.")
            if self.engine:
                self.engine.dispose()
                print("Database engine disposed successfully.")
        except Exception as e:
            print(f"Error disconnecting from the database: {e}")
        finally:
            # Optionally set self.connection and self.engine to None after closing
            self.connection = None
            self.engine = None

    def fetch_data(self, sql_template, params=None, batch_size=100):
        """For collecting data and using it"""
        template = Template(sql_template)
        conn = self.connect_to_database()
        sql_query = template.render(params or {})
        cursor = conn.execute(text(sql_query))
        while True:
            rows = cursor.fetchmany(batch_size)
            if not rows:
                break
            yield rows

        cursor.close()
        conn.close()

    def query_data(self, sql_template, params=None):
        try:
            conn = self.connect_to_database()
            template = Template(sql_template)
            sql_query = template.render(params or {})
            cursor = conn.execute(text(sql_query))
            result = cursor.fetchall()
            cursor.close()
            self.disconnect()
            return result
        except Exception as e:
            print(f"Failed to query data from the database; more info -> {e}")
            return None


class EdgarQueryManager:
    def __init__(self):
        load_dotenv()
        self.sec_api_key = os.getenv("SEC_API_KEY")

    def extract_section_data(self, filing_url: str, section: str):
        extractor_api = ExtractorApi(self.sec_api_key)
        section_data = extractor_api.get_section(
            filing_url=filing_url, section=section, return_type="text"
        )
        return section_data

    def mapping_api_data(self, key: str, value: str):
        """Where key is one of the keys in the json response and the value is the searchable value;
        ie: name: Tesla Inc | ticker: TSLA | cik: 1318605 | exchange: NASDAQ"""
        mapping_api = MappingApi(self.sec_api_key)
        result = mapping_api.resolve(key, value)
        return result

    def mapping_data(self, key: str, value: str):
        db = ConnectionManager()
        db.connect_to_database()
        data = self.mapping_api_data(key=key, value=value)
        db.insert_json_data(table_name="security_details", json_response=data)

    def security_data(self, exchange_list: list):
        for exchange in exchange_list:
            self.mapping_data(key="exchange", value=exchange)

    def filing_url_collection(self, ticker: str, section: str, size: str):
        """Makes 1 API call per ticker, grabs the filing url information for the last 50 filings,
        includes 10-k and 10-k/a data in the new staging table (historic_filing_urls)"""

        ticker = ticker.upper()
        queryApi = QueryApi(api_key=self.sec_api_key)
        query = {
            "query": {
                "query_string": {
                    "query": f'''ticker:{ticker} AND formType:\"{section}\"'''
                }
            },
            "from": "0",
            "size": f'''"{size}"''',  # max number of filing urls returned
            "sort": [{"filedAt": {"order": "desc"}}],
        }
        response = queryApi.get_filings(query)

        filings = response["filings"]
        db = ConnectionManager()
        db.connect_to_database()
        for filing in filings:
            ticker = filing.get("ticker")
            filing_url = filing.get(
                "linkToHtml", ""
            )  # Assuming the URL attribute is 'url'
            text_version = filing.get("linkToTxt", "")
            index_filing = filing.get("linkToFilingDetails", "")
            filed_at = filing.get("filedAt", "")
            form = filing.get("formType", "")
            cik = filing.get("cik", "")
            company_name = filing.get("companyName", "")
            data = {
                "ticker": ticker,
                "filing_url": filing_url,
                "text_version_filing": text_version,
                "index_page_filing": index_filing,
                "date": filed_at,
                "form": form,
                "cik": cik,
                "company_name": company_name,
            }
            db.insert_data(table_name="historic_filing_urls", data=data)

    def ten_k_collection(
        self, db, ticker: str, filing_url: str, date: datetime
    ) -> None:
        """This function grabs the entire 10k from the SEC API (currently makes 20 API calls per form)"""
        try:
            db.connect_to_database()
            db.insert_data(
                table_name="raw_ten_k_data",
                data={
                    "ticker": f"{ticker}",
                    "filing_date": f"{date}",
                    "filing_url": f"{filing_url}",
                    "section_one": f"{self.extract_section_data(filing_url=filing_url, section='1')}",
                    "section_one_a": f"{self.extract_section_data(filing_url=filing_url, section='1A')}",
                    "section_one_b": f"{self.extract_section_data(filing_url=filing_url, section='1B')}",
                    "section_two": f"{self.extract_section_data(filing_url=filing_url, section='2')}",
                    "section_three": f"{self.extract_section_data(filing_url=filing_url, section='3')}",
                    "section_four": f"{self.extract_section_data(filing_url=filing_url, section='4')}",
                    "section_five": f"{self.extract_section_data(filing_url=filing_url, section='5')}",
                    "section_six": f"{self.extract_section_data(filing_url=filing_url, section='6')}",
                    "section_seven": f"{self.extract_section_data(filing_url=filing_url, section='7')}",
                    "section_seven_a": f"{self.extract_section_data(filing_url=filing_url, section='7A')}",
                    "section_eight": f"{self.extract_section_data(filing_url=filing_url, section='8')}",
                    "section_nine": f"{self.extract_section_data(filing_url=filing_url, section='9')}",
                    "section_nine_a": f"{self.extract_section_data(filing_url=filing_url, section='9A')}",
                    "section_nine_b": f"{self.extract_section_data(filing_url=filing_url, section='9B')}",
                    "section_ten": f"{self.extract_section_data(filing_url=filing_url, section='10')}",
                    "section_eleven": f"{self.extract_section_data(filing_url=filing_url, section='11')}",
                    "section_twelve": f"{self.extract_section_data(filing_url=filing_url, section='12')}",
                    "section_thirteen": f"{self.extract_section_data(filing_url=filing_url, section='13')}",
                    "section_fourteen": f"{self.extract_section_data(filing_url=filing_url, section='14')}",
                    "section_fifteen": f"{self.extract_section_data(filing_url=filing_url, section='15')}",
                    "created_at": f"{datetime.datetime.now()}",
                    "updated_at": f"{datetime.datetime.now()}",
                },
            )
        finally:
            db.disconnect()

    def ten_q_collection(
        self, db, ticker: str, filing_url: str, date: datetime
    ) -> None:
        """This function collects the information for 10-q data from the SEC API"""
        try:
            db.connect_to_database()
            db.insert_data(
                table_name="raw_ten_q_data",
                data={
                    "ticker": f"{ticker}",
                    "filing_date": f"{date}",
                    "filing_url": f"{filing_url}",
                    "part_1_item_1": f"{self.extract_section_data(filing_url=filing_url,section='part1item1')}",
                    "part_1_item_2": f"{self.extract_section_data(filing_url=filing_url, section='part1item2')}",
                    "part_1_item_3": f"{self.extract_section_data(filing_url=filing_url, section='part1item3')}",
                    "part_1_item_4": f"{self.extract_section_data(filing_url=filing_url, section='part1item4')}",
                    "part_2_item_1": f"{self.extract_section_data(filing_url=filing_url, section='part2item1')}",
                    "part_2_item_1a": f"{self.extract_section_data(filing_url=filing_url, section='part2item1a')}",
                    "part_2_item_2": f"{self.extract_section_data(filing_url=filing_url, section='part2item2')}",
                    "part_2_item_3": f"{self.extract_section_data(filing_url=filing_url, section='part2item3')}",
                    "part_2_item_4": f"{self.extract_section_data(filing_url=filing_url, section='part2item4')}",
                    "part_2_item_5": f"{self.extract_section_data(filing_url=filing_url, section='part2item5')}",
                    "part_2_item_6": f"{self.extract_section_data(filing_url=filing_url, section='part2item6')}",
                },
            )
        finally:
            db.disconnect()

    def eight_k_collection(
        self, db, ticker: str, filing_url: str, date: datetime
    ) -> None:
        try:
            db.connect_to_database()
            db.insert_data(
                table_name="raw_ten_q_data",
                data={
                    "ticker": f"{ticker}",
                    "filing_date": f"{date}",
                    "filing_url": f"{filing_url}",
                    "one_one": f"{self.extract_section_data(filing_url=filing_url, section='1-1')}",
                    "one_two": f"{self.extract_section_data(filing_url=filing_url, section='1-2')}",
                    "one_three": f"{self.extract_section_data(filing_url=filing_url, section='1-3')}",
                    "one_four": f"{self.extract_section_data(filing_url=filing_url, section='1-4')}",
                    "one_five": f"{self.extract_section_data(filing_url=filing_url, section='1-5')}",
                    "two_one": f"{self.extract_section_data(filing_url=filing_url, section='2-1')}",
                    "two_two": f"{self.extract_section_data(filing_url=filing_url, section='2-2')}",
                    "two_three": f"{self.extract_section_data(filing_url=filing_url, section='2-3')}",
                    "two_four": f"{self.extract_section_data(filing_url=filing_url, section='2-4')}",
                    "two_five": f"{self.extract_section_data(filing_url=filing_url, section='2-5')}",
                    "two_six": f"{self.extract_section_data(filing_url=filing_url, section='2-6')}",
                    "three_one": f"{self.extract_section_data(filing_url=filing_url, section='3-1')}",
                    "three_two": f"{self.extract_section_data(filing_url=filing_url, section='3-2')}",
                    "three_three": f"{self.extract_section_data(filing_url=filing_url, section='3-3')}",
                    "four_one": f"{self.extract_section_data(filing_url=filing_url, section='4-1')}",
                    "four_two": f"{self.extract_section_data(filing_url=filing_url, section='4-2')}",
                    "five_one": f"{self.extract_section_data(filing_url=filing_url, section='5-1')}",
                    "five_two": f"{self.extract_section_data(filing_url=filing_url, section='5-2')}",
                    "five_three": f"{self.extract_section_data(filing_url=filing_url, section='5-3')}",
                    "five_four": f"{self.extract_section_data(filing_url=filing_url, section='5-4')}",
                    "five_five": f"{self.extract_section_data(filing_url=filing_url, section='5-5')}",
                    "five_six": f"{self.extract_section_data(filing_url=filing_url, section='5-6')}",
                    "five_seven": f"{self.extract_section_data(filing_url=filing_url, section='5-7')}",
                    "five_eight": f"{self.extract_section_data(filing_url=filing_url, section='5-8')}",
                    "six_one": f"{self.extract_section_data(filing_url=filing_url, section='6-1')}",
                    "six_two": f"{self.extract_section_data(filing_url=filing_url, section='6-2')}",
                    "six_three": f"{self.extract_section_data(filing_url=filing_url, section='6-3')}",
                    "six_four": f"{self.extract_section_data(filing_url=filing_url, section='6-4')}",
                    "six_five": f"{self.extract_section_data(filing_url=filing_url, section='6-5')}",
                    "six_six": f"{self.extract_section_data(filing_url=filing_url, section='6-6')}",
                    "six_ten": f"{self.extract_section_data(filing_url=filing_url, section='6-10')}",
                    "seven_one": f"{self.extract_section_data(filing_url=filing_url, section='7-1')}",
                    "eight_one": f"{self.extract_section_data(filing_url=filing_url, section='8-1')}",
                    "nine_one": f"{self.extract_section_data(filing_url=filing_url, section='9-1')}",
                    "signature": f"{self.extract_section_data(filing_url=filing_url, section='signature')}",
                },
            )
        finally:
            db.disconnect()

    def threaded_filing_url_collection(self, tickers: list, section, size):
        db = ConnectionManager()

        def thread_wrapper(args):
            tickers, section, size = args
            try:
                self.filing_url_collection(
                    db, ticker=tickers, section=section, size=size
                )
            except Exception as e:
                print(f"Error in thread: {e}")

        with ThreadPoolExecutor(
            max_workers=8
        ) as executor:  # Set the desired number of threads
            executor.map(thread_wrapper, tickers)

    def threaded_ten_k_collection(self, tickers_and_urls: list, form_type: str):
        """Process the 10k collection in multiple threads"""
        db = ConnectionManager()  # Each thread should have its own database connection

        def thread_wrapper(args):
            ticker, filing_url, date = args
            try:
                if form_type == "10k":
                    self.ten_k_collection(db, ticker, filing_url, date)
                elif form_type == "10q":
                    self.ten_q_collection(db, ticker, filing_url, date)
                elif form_type == "8k":
                    self.eight_k_collection(db, ticker, filing_url, date)
            except Exception as e:
                print(f"Error in thread: {e}")

        # Use ThreadPoolExecutor to control the number of threads
        with ThreadPoolExecutor(
            max_workers=8
        ) as executor:  # Set the desired number of threads
            executor.map(thread_wrapper, tickers_and_urls)
