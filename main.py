#!/usr/bin/env python3

import argparse
import httpx
import xml.etree.ElementTree as ET
from variables import ELINK_URL, ESUMMARY_URL
from sklearn.feature_extraction.text import TfidfVectorizer


def get_data_from_txt(file_path: str) -> list[str] | None:
    try:
        with open(file_path, "r") as file:
            return [x.strip() for x in file.readlines()]
    except FileNotFoundError:
        print(f"File {file_path} not found")


def get_datasets_id(index: str, key : str) -> list[str]:
    print(index)
    request_url = f"{ELINK_URL}&id={index}"
    if key:
        request_url = request_url + f"&key={key}"
    response = httpx.get(request_url)
    xml_root = ET.fromstring(response.text)
    return [idx.text for idx in xml_root.findall(".//Link/Id")]


def request_from_database(dataset: str, pimd: str, key : str = None) -> dict[str, str]:
    print(dataset)
    request_url = f"{ESUMMARY_URL}&id={dataset}"
    if key:
        request_url = request_url + f"&key={key}"
    response = httpx.get(request_url)
    xml_root = ET.fromstring(response.text)
    d = {
        'pimd' : pimd,
        'dataset' : dataset,
        'title' : xml_root.find(".//Item[@Name='title']").text,
        'experiment type' : xml_root.find(".//Item[@Name='gdsType']").text,
        'summary' : xml_root.find(".//Item[@Name='summary']").text,
        'organism' : xml_root.find(".//Item[@Name='taxon']").text
        # todo overall design
    }
    print(d)
    return d

def tfidf(data: list[str]):
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(data)
    tfidf_array = tfidf_matrix.toarray()
    return tfidf_array


def main():
    parser = argparse.ArgumentParser(description='Program to retrieve information from PubMed')
    parser.add_argument('-f', '--file', required=True, type=str, help='Path to .txt file with PMIDs')
    parser.add_argument('-k', '--key', required=False, type=str, help='Api key for eutils')
    args = parser.parse_args()
    pimd = get_data_from_txt(args.file)
    print("pimd: ", pimd)
    for p in pimd:
        ids = get_datasets_id(p, args.key)
        print("ids: ", ids)
        for i in ids:
            request_from_database(i, args.key)


if __name__ == "__main__":
    main()