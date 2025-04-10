select ticker, text_version_filing as filing_url, date
from historic_filing_urls
where form like '{{form_type}}%';