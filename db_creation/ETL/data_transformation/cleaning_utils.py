from shared_utils.connection_management import ConnectionManager
class Cleaner:
    def __init__(self):
        pass

    @staticmethod
    def remove_item_markers(text: str) -> str:
        """Need to spend some time removing the item markers that are present at the start of each text blob (ITEM 1)"""
        item_markers = {
            "ITEM 1 BUSINESS OVERVIEW",
            "Item 1 Business Overview",
            "1A. Risk Factors.",
            "1A. Ri sk Factors.",
            "ITEM 1B. UNRESOLVED STAFF COMMENTS",
            "Item 1B. Unresolved Staff Comments",
            "ITEM 2. PROPERTIES",
            "Item 2. Properties",
            "ITEM 3. LEGAL PROCEEDINGS",
            "Item 3. Legal Proceedings" "ITEM 4. MINE SAFETY DISCLOSURES",
            "ITEM 4.  SUBMISSION OF MATTERS TO A VOTE OF UNITHOLDERS",
            "Item 4. Submission of Matters to a Vote of Security Holders. ",
            "ITEM 5.   MARKET FOR REGISTRANT'S COMMON EQUITY AND RELATED STOCKHOLDER MATTERS.",
            "Item  5.  Market for the Registrant's Common Stock and Related Stockholder Matters",
            "Item 6. SELECTED FINANCIAL DATA ",
            " Item 6. Selected Financial Data ",
            "ITEM 7 MANAGEMENT&#146;S DISCUSSION AND ANALYSIS OF FINANCIAL CONDITION AND RESULTS OF OPERATIONS ",
            " Item 7. Management&#8217;s Discussion and Analysis of Financial Condition and Results of Operations.",
            "Item 7A. Quantitative and Qualitative Disclosures about Market Risk ",
            "ITEM 7A. QUANTITATIVE AND QUALITATIVE DISCLOSURE ABOUT MARKET RISK.",
            "Item 8. Financial Statements and Supplementary Data ",
            " ITEM 8&#8212;FINANCIAL STATEMENTS AND SUPPLEMENTARY DATA",
            "Item 9. Changes in and Disagreements with Accountants on Accounting and Financial Disclosure ",
            "ITEM 9. CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCED DISCLOSURE",
            "ITEM 9A. &#160; CONTROLS AND PROCEDURES ##TABLE_END &#160",
            "Item 9A. Controls and Procedures",
            "Item 9B. Other Information ",
            "Item 9B. OTHER INFORMATION",
            "Item 10. Directors, Executive Officers and Corporate Governance.",
            "ITEM 10. &#160; DIRECTORS, EXECUTIVE OFFICERS AND CORPORATE GOVERNANCE ",
            "Item 11. Executive Compensation",
            "ITEM 11. EXECUTIVE COMPENSATION",
            "ITEM 12. SECURITY OWNERSHIP OF CERTAIN BENEFICIAL OWNERS AND MANAGEMENT.",
            "Item 12. Security Ownership of Certain Beneficial Owners and Management and Related Shareholder Matters.",
            "Item 13. Certain Relationships and Related Transactions, and Director Independence",
            "ITEM 13. CERTAIN RELATIONSHIPS AND RELATED TRANSACTIONS AND DIRECTOR INDEPENDENCE",
            "Item 14. Exhibits, Financial Statement Schedules, and Reports on Form 8-k",
            "ITEM 14.  EXHIBITS, FINANCIAL STATEMENT SCHEDULES, AND REPORTS ON FORM 8-K",
            " Item 15. Exhibits, Financial Statement Schedules",
            "ITEM 15. EXHIBITS AND FINANCIAL STATEMENT SCHEDULES",
        }
        for item in item_markers:
            text = text.replace(item, "")
        return text

    @staticmethod
    def replace_empty_fields(text: str) -> str:
        """Not all the fields were populated in ingestion,
        need to swap an empty field for NaN or a placeholder of sorts"""
        if text is None or text == "":
            text = "lorem ipsum"
        return text

    @staticmethod
    def to_lowercase(text: str) -> str:
        """Remove the difference between capitals and lowercase across the string, make it all lowercase"""
        return text.lower()

    @staticmethod
    def remove_table_strings(text: str) -> str:
        """Often times we run into an issue of leftovers table strings in the text blocks (mainly in 10-Q files)
        when doc was converted from rich to plain text
            Examples include:
        """
        unicode_trash = {
            "&#8221",
            "&#8203",
            "&#160",
            "$",
            "&#8212",
            "&#8217",
            "&#38",
            "&#8220",
            "&#148",
            "&#149",
            "&#146",
            "##table_start ",
            "##table_end ",
            "&#151",
            "&#174",
            "&#147",
            "&#225",
            "##",
            "table_start",
            "table_end"
        }
        for trash in unicode_trash:
            text = text.replace(trash, "")
        return text
