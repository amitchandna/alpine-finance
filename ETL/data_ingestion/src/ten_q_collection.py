from shared_utils.connection_management import ConnectionManager, EdgarQueryManager


def ten_q_collection() -> None:
    """Collects the Ten Q files for all values in the historic filing table"""
    db = ConnectionManager()
    sec_api = EdgarQueryManager()
    with open(
        "../sql/filing_url_data.sql",
        "r",
    ) as sql:
        sql_query = sql.read()
        data = db.fetch_data(
            sql_template=sql_query, params={"form_type": "10-Q"}, batch_size=1
        )
        tickers_and_urls = [(row[0][0], row[0][1], row[0][2]) for row in data]
        sec_api.threaded_ten_k_collection(
            tickers_and_urls=tickers_and_urls, form_type="10q"
        )
