import pandas as pd


def extract_tables(url):

    tables = pd.read_html(url)

    return tables