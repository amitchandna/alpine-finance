from shared_utils.connection_management import ConnectionManager, EdgarQueryManager


def ten_k_collection() -> None:
    """Collects Ten K Forms for all values in the historical filing table"""
    db = ConnectionManager()
    sec_api = EdgarQueryManager()
    with open(
        "../sql/filing_url_data.sql",
        "r",
    ) as sql:
        sql_query = sql.read()
        data = db.fetch_data(sql_template=sql_query, params={}, batch_size=1)
        tickers_and_urls = [(row[0][0], row[0][1], row[0][2]) for row in data]
        sec_api.threaded_ten_k_collection(
            tickers_and_urls=tickers_and_urls, form_type="10k"
        )
