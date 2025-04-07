import httpx
import xml.etree.ElementTree as ET
import time

from variables import ELINK_URL, ESUMMARY_URL, EGSE_URL
from logs import log


def get_data_from_txt(file_path: str) -> list[str]:
    """
    Function to get PMIDs from txt file

    :param file_path: Path to text file with PMIDs
    :return: List of PMIDs
    """
    log("Stage", f"Running get_data_from_txt(file_path={file_path})...")
    try:
        with open(file_path, "r") as file:
            return [x.strip() for x in file.readlines()]
    except FileNotFoundError:
        log("Exception", f"File {file_path} not found")
        return []


def get_datasets_id(index: str, key : str) -> list[str]:
    """
    Function to extract ids from given PIMD data

    :param index: PIMD index
    :param key: Api key for faster data retrieval
    :return: List of links to GEO id
    """
    log("Stage", f"Running get_datasets_id(index={index}, key={bool(key)})...")
    request_url = f"{ELINK_URL}&id={index}"
    if key:
        request_url = request_url + f"&key={key}"
    response = None
    while response is None or response.status_code == 429:
        try:
            response = httpx.get(request_url)
        except httpx.TimeoutException as e:
            log("Exception", f"{e}")
            continue
        except httpx.HTTPError as e:
            log("Exception", f"{e}")
            return []
        time.sleep(1)
    xml_root = ET.fromstring(response.text)
    data = [idx.text for idx in xml_root.findall(".//Link/Id")]
    return data


def request_from_database(dataset: str, pimd: str, key : str = None) -> dict[str, str]:
    """
    Function to retrieve data from given GEO id

    :param dataset: GEO id that
    :param pimd: PIMD which GEO was retrieved from
    :param key: Api key for faster data retrieval
    :return: Dictionary of data needed to create sample text
    """
    log("Stage", f"Running request_from_database(dataset={dataset}, pimd={pimd}, key={bool(key)})...")
    request_url = f"{ESUMMARY_URL}&id={dataset}"
    if key:
        request_url = request_url + f"&key={key}"
    response = None
    while response is None or response.status_code == 429:
        try:
            response = httpx.get(request_url)
        except httpx.TimeoutException as e:
            log("Exception", f"{e}")
            continue
        except httpx.HTTPError as e:
            log("Exception", f"{e}")
            return {}
        time.sleep(1)
    xml_root = ET.fromstring(response.text)
    gse = "GSE" + xml_root.find(".//Item[@Name='GSE']").text
    gse_txt = httpx.get(f"{EGSE_URL}&acc={gse}")
    overall_design = " ".join(
        line.replace("!Series_overall_design = ", "")
            .replace(".  ", ".")
            .strip()
        for line in gse_txt.text.splitlines()
        if line.startswith("!Series_overall_design")
    )
    log("Stage", f"Preparing data from id {gse}...")
    d = {
        'pimd'              : pimd,
        'dataset'           : dataset,
        'title'             : xml_root.find(".//Item[@Name='title']").text,
        'experiment type'   : xml_root.find(".//Item[@Name='gdsType']").text,
        'summary'           : xml_root.find(".//Item[@Name='summary']").text,
        'organism'          : xml_root.find(".//Item[@Name='taxon']").text,
        'overall_design'    : overall_design
    }
    log("Data", d)
    return d
