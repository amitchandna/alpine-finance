from shared_utils.connection_management import EdgarQueryManager, ConnectionManager


def filing_url_population() -> None:
    """Collects the values for a filing url table"""
    db = ConnectionManager()
    sec_api = EdgarQueryManager()

    with open(
        "../sql/ten_q_securities.sql",
        "r",
    ) as sql:
        sql_query = sql.read()
        data = db.fetch_data(sql_template=sql_query)
        for data_row in data:
            sec_api.filing_url_collection(
                ticker=data_row[0][0], section="10-Q", size="20"
            )
            sec_api.filing_url_collection(
                ticker=data_row[0][0], section="8-K", size="20"
            )
