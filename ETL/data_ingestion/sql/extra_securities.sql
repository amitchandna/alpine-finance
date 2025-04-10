select ticker
from security_details sd
where sd.ticker not in (select distinct(hfu.ticker) from historic_filing_urls hfu)