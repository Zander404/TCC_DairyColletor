import os
from dotenv import load_dotenv


load_dotenv()


# GERAL
API_KEY = os.getenv("API_KEY")
# KEYWORDS_LIST = ["dairy", "dairy cows", "dairy farming", "dairies"]
KEYWORDS_LIST = ["Journal of dairy science"]
KEYWORDS = "+".join(KEYWORDS_LIST)


# URLS
URL_PUBMED = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

URL_SEARCH: str = f"{URL_PUBMED}/esearch.fcgi?&api_key={
    API_KEY
}&db=pubmed&retmode=json&term={KEYWORDS}&retmax="

URL_FETCH: str = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?api_key={
    API_KEY
}&db=pubmed&rettype=abstract&id="


# COLLUNS
COLLUMS = [
    "PubMedID",
    "DOI",
    "PII",
    "URL",
    "Journal",
    "Title",
    "Abstract",
    "Author",
    "Year",
    "Keywords",
]
