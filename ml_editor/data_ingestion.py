import xml.etree.ElementTree as Elt
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import os


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


def get_data_from_dump(site_name, load_existing=True):
    """
    load .xml dump from site, parse it to csv, serialize it
    :param site_name: stackexchange website name
    :param load_existing: load existing data or recreate it
    :return: pandas DataFrame
    """

    data_path = Path("data")
    dump_name = site_name + ".stackexchange.com/Posts.xml"
    file_name = site_name + ".csv"
    dump_path = data_path/dump_name
    file_path = data_path/file_name

    if not (load_existing and os.path.isfile(file_path)):
        data = parse_xml_to_csv(dump_path)
        data.to_csv(file_path)
    else:
        data = pd.DataFrame.from_csv(file_path)

    return data
