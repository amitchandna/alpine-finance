"""
Database models for Alpine Finance RAG system.
"""
from django.db import models
from pgvector.django import VectorField
from django.db import models


class SecurityDetails(models.Model):
    name = models.TextField()
    ticker = models.TextField()
    cik = models.TextField()
    cusip = models.TextField()
    exchange = models.TextField()
    isDelisted = models.BooleanField()
    category = models.TextField()
    sector = models.TextField()
    industry = models.TextField()
    sic = models.TextField()
    sicSector = models.TextField()
    sicIndustry = models.TextField()
    currency = models.TextField()
    location = models.TextField()
    sec_id = models.TextField()

    class Meta:
        db_table = "security_details"


class TenKData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_one = models.TextField()
    section_one_a = models.TextField()
    section_one_b = models.TextField()
    section_two = models.TextField()
    section_three = models.TextField()
    section_four = models.TextField()
    section_five = models.TextField()
    section_six = models.TextField()
    section_seven = models.TextField()
    section_seven_a = models.TextField()
    section_eight = models.TextField()
    section_nine = models.TextField()
    section_nine_a = models.TextField()
    section_nine_b = models.TextField()
    section_ten = models.TextField()
    section_eleven = models.TextField()
    section_twelve = models.TextField()
    section_thirteen = models.TextField()
    section_fourteen = models.TextField()
    section_fifteen = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "raw_ten_k_data"


class FilingUrls(models.Model):
    ticker = models.TextField()
    filing_url = models.TextField()
    text_version_filing = models.TextField()
    index_page_filing = models.TextField()
    date = models.TextField()
    form = models.TextField()
    cik = models.TextField()
    company_name = models.TextField()

    class Meta:
        db_table = "historic_filing_urls"


class TenQData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    part_1_item_1 = models.TextField()
    part_1_item_2 = models.TextField()
    part_1_item_3 = models.TextField()
    part_1_item_4 = models.TextField()
    part_2_item_1 = models.TextField()
    part_2_item_1a = models.TextField()
    part_2_item_2 = models.TextField()
    part_2_item_3 = models.TextField()
    part_2_item_4 = models.TextField()
    part_2_item_5 = models.TextField()
    part_2_item_6 = models.TextField()

    class Meta:
        db_table = "raw_ten_q_data"


class EightKData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    one_one = models.TextField()
    one_two = models.TextField()
    one_three = models.TextField()
    one_four = models.TextField()
    one_five = models.TextField()
    two_one = models.TextField()
    two_two = models.TextField()
    two_three = models.TextField()
    two_four = models.TextField()
    two_five = models.TextField()
    two_six = models.TextField()
    three_one = models.TextField()
    three_two = models.TextField()
    three_three = models.TextField()
    four_one = models.TextField()
    four_two = models.TextField()
    five_one = models.TextField()
    five_two = models.TextField()
    five_three = models.TextField()
    five_four = models.TextField()
    five_five = models.TextField()
    five_six = models.TextField()
    five_seven = models.TextField()
    five_eight = models.TextField()
    six_one = models.TextField()
    six_two = models.TextField()
    six_three = models.TextField()
    six_four = models.TextField()
    six_five = models.TextField()
    six_six = models.TextField()
    six_ten = models.TextField()
    seven_one = models.TextField()
    eight_one = models.TextField()
    nine_one = models.TextField()
    signature = models.TextField()

    class Meta:
        db_table = "raw_eight_k_data"


class ProcessedTenKData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_one = models.TextField()
    section_one_a = models.TextField()
    section_one_b = models.TextField()
    section_two = models.TextField()
    section_three = models.TextField()
    section_four = models.TextField()
    section_five = models.TextField()
    section_six = models.TextField()
    section_seven = models.TextField()
    section_seven_a = models.TextField()
    section_eight = models.TextField()
    section_nine = models.TextField()
    section_nine_a = models.TextField()
    section_nine_b = models.TextField()
    section_ten = models.TextField()
    section_eleven = models.TextField()
    section_twelve = models.TextField()
    section_thirteen = models.TextField()
    section_fourteen = models.TextField()
    section_fifteen = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processed_ten_k_data"


class ProcessedTenQData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    part_1_item_1 = models.TextField()
    part_1_item_2 = models.TextField()
    part_1_item_3 = models.TextField()
    part_1_item_4 = models.TextField()
    part_2_item_1 = models.TextField()
    part_2_item_1a = models.TextField()
    part_2_item_2 = models.TextField()
    part_2_item_3 = models.TextField()
    part_2_item_4 = models.TextField()
    part_2_item_5 = models.TextField()
    part_2_item_6 = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processed_ten_q_data"


class ProcessedEightKData(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    one_one = models.TextField()
    one_two = models.TextField()
    one_three = models.TextField()
    one_four = models.TextField()
    one_five = models.TextField()
    two_one = models.TextField()
    two_two = models.TextField()
    two_three = models.TextField()
    two_four = models.TextField()
    two_five = models.TextField()
    two_six = models.TextField()
    three_one = models.TextField()
    three_two = models.TextField()
    three_three = models.TextField()
    four_one = models.TextField()
    four_two = models.TextField()
    five_one = models.TextField()
    five_two = models.TextField()
    five_three = models.TextField()
    five_four = models.TextField()
    five_five = models.TextField()
    five_six = models.TextField()
    five_seven = models.TextField()
    five_eight = models.TextField()
    six_one = models.TextField()
    six_two = models.TextField()
    six_three = models.TextField()
    six_four = models.TextField()
    six_five = models.TextField()
    six_six = models.TextField()
    six_ten = models.TextField()
    seven_one = models.TextField()
    eight_one = models.TextField()
    nine_one = models.TextField()
    signature = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "processed_eight_k_data"


class ProcessedTenKSectionOne(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_one = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_one"


class ProcessedTenKSectionOneA(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_one_a = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_one_a"


class ProcessedTenKSectionOneB(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_one_b = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_one_b"


class ProcessedTenKSectionTwo(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_two = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_two"


class ProcessedTenKSectionThree(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_three = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_three"


class ProcessedTenKSectionFour(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_four = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_four"


class ProcessedTenKSectionFive(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_five = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_five"


class ProcessedTenKSectionSix(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_six = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_six"


class ProcessedTenKSectionSeven(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_seven = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_seven"


class ProcessedTenKSectionSevenA(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_seven_a = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_seven_a"


class ProcessedTenKSectionEight(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_eight = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_eight"


class ProcessedTenKSectionNine(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_nine = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_nine"


class ProcessedTenKSectionNineA(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_nine_a = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_nine_a"


class ProcessedTenKSectionNineB(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_nine_b = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_nine_b"


class ProcessedTenKSectionTen(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_ten = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_ten"


class ProcessedTenKSectionEleven(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_eleven = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_eleven"


class ProcessedTenKSectionTwelve(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_twelve = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_twelve"


class ProcessedTenKSectionThirteen(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_thirteen = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_thirteen"


class ProcessedTenKSectionFourteen(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_fourteen = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_fourteen"


class ProcessedTenKSectionFifteen(models.Model):
    ticker = models.CharField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    section_fifteen = models.TextField()

    class Meta:
        db_table = "processed_ten_k_section_fifteen"


# Small Embeddings (384 dimensions)
class RAGFilingSectionSmall(models.Model):
    """Filing sections for small embeddings (384-dim)"""
    
    id = models.AutoField(primary_key=True)
    filing_type = models.TextField()
    ticker = models.TextField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    source_table = models.TextField()
    source_column = models.TextField()
    section_name = models.TextField()
    full_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_filing_sections_small"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]


class RAGChunkSmall(models.Model):
    """Text chunks for small embeddings (384-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionSmall,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_384 = VectorField(dimensions=384, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_small"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]


# Medium Embeddings (768 dimensions)
class RAGFilingSectionMedium(models.Model):
    """Filing sections for medium embeddings (768-dim)"""
    
    id = models.AutoField(primary_key=True)
    filing_type = models.TextField()
    ticker = models.TextField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    source_table = models.TextField()
    source_column = models.TextField()
    section_name = models.TextField()
    full_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_filing_sections_medium"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]


class RAGChunkMedium(models.Model):
    """Text chunks for medium embeddings (768-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionMedium,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_768 = VectorField(dimensions=768, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_medium"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]


# Large Embeddings (1024 dimensions)
class RAGFilingSectionLarge(models.Model):
    """Filing sections for large embeddings (1024-dim)"""
    
    id = models.AutoField(primary_key=True)
    filing_type = models.TextField()
    ticker = models.TextField()
    filing_date = models.DateField()
    filing_url = models.TextField()
    source_table = models.TextField()
    source_column = models.TextField()
    section_name = models.TextField()
    full_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_filing_sections_large"
        indexes = [
            models.Index(fields=["ticker", "filing_type", "section_name"]),
        ]


class RAGChunkLarge(models.Model):
    """Text chunks for large embeddings (1024-dim)"""
    
    id = models.AutoField(primary_key=True)
    section = models.ForeignKey(
        RAGFilingSectionLarge,
        on_delete=models.CASCADE,
        related_name='chunks',
        db_column='section_id'
    )
    chunk_index = models.IntegerField()
    text = models.TextField()
    token_count = models.IntegerField()
    embedding_1024 = VectorField(dimensions=1024, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "rag_chunks_large"
        indexes = [
            models.Index(fields=["section", "chunk_index"]),
        ]
