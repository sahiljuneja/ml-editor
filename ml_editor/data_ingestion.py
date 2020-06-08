import xml.etree.ElementTree as Elt
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd


def parse_xml_to_csv(path, save_path=None):
    """
    open .xml posts dump, tokenize text, and convert it into csv
    :param path: path to xml document containing posts
    :param save_path: path to save csv
    :return: dataframe of processed text
    """

    # parse XML using python's standard lib
    doc = Elt.parse(path)
    root = doc.getroot()

    # each row is a question
    rows = [row.attrib for row in root.findall("row")]

    # use tdqm to display progress
    for item in tqdm(rows):
        # decode HTML text
        soup = BeautifulSoup(item["Body"], features="html.parser")
        item["body_text"] = soup.get_text()

    # create dataframe from dict
    df = pd.DataFrame.from_dict(rows)
    if save_path:
        df.to_csv(save_path)

    return df
