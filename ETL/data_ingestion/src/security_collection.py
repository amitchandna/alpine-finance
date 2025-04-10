from shared_utils.connection_management import EdgarQueryManager, ConnectionManager


def populate_security_table() -> None:
    """This is to populate the security table if it is empty, it will just pull as many values as possible"""
    db = ConnectionManager()
    sec_api = EdgarQueryManager()

    with open(
        "../sql/security_list.sql",
        "r",
    ) as sql:
        sql_query = sql.read()
        # NASDAQ Collection
        data = db.fetch_data(
            sql_template=sql_query, params={"exchange": "NASDAQ"}, batch_size=1
        )
        for data_row in data:
            sec_api.filing_url_collection(ticker=data_row[0][0])

        # NYSE Collection
        data = db.fetch_data(
            sql_template=sql_query, params={"exchange": "NYSE"}, batch_size=1
        )
        for data_row in data:
            sec_api.filing_url_collection(ticker=data_row[0][0])

        # NYSEMKT Collection
        data = db.fetch_data(
            sql_template=sql_query, params={"exchange": "NYSEMKT"}, batch_size=1
        )
        for data_row in data:
            sec_api.filing_url_collection(ticker=data_row[0][0])

        # NYSEARCA Collection
        data = db.fetch_data(
            sql_template=sql_query, params={"exchange": "NYSEARCA"}, batch_size=1
        )
        for data_row in data:
            sec_api.filing_url_collection(ticker=data_row[0][0])


def extra_security_collection() -> None:
    """This collects the difference between the security table and the historic filing url table set"""
    db = ConnectionManager()
    sec_api = EdgarQueryManager()
    with open(
        "../sql/extra_securities.sql",
        "r",
    ) as sql:
        sql_query = sql.read()
        data = db.fetch_data(sql_template=sql_query)
        for data_row in data:
            sec_api.filing_url_collection(ticker=data_row[0][0])
