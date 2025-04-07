#!/usr/bin/env python3

import argparse
import concurrent.futures

from retrieve_data import get_data_from_txt, get_datasets_id, request_from_database
from ml import tf_idf_sklearn, similarity, clustering_kmeans, plot_clusters
from logs import log


def get_arguments() -> argparse.Namespace:
    """
    Function for retrieving arguments from user

    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Program to retrieve information from PubMed')
    parser.add_argument('-f', '--file', required=True, type=str, help='Path to .txt file with PMIDs')
    parser.add_argument('-k', '--key', required=False, type=str, help='Api key for eutils')
    return parser.parse_args()


def process_pmid(pmid: str, key: str) -> tuple[str, int, list[dict[str, str]]]:
    """
    Single process of retrieving information from PubMed

    :param pmid: PIMD index
    :param key: Api key for faster data retrieval
    :return:
    """
    ids = get_datasets_id(pmid, key)
    log("Data", ids)
    retrieved_ids = 0
    data_list = []
    for i in ids:
        data_dict = request_from_database(i, pmid, key)
        if data_dict:
            retrieved_ids += 1
            data_list.append(data_dict)
    return pmid, retrieved_ids, data_list


def main(args: argparse.Namespace) -> None:
    """
    Main logic of program

    :param args: Parsed arguments from user
    :return:
    """
    pimd = get_data_from_txt(args.file)
    log("Data", {'PIMD': pimd})
    results = {}

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_pmid = {executor.submit(process_pmid, p, args.key): p for p in pimd}
        for future in concurrent.futures.as_completed(future_to_pmid):
            pmid, retrieved_ids, data_list = future.result()
            results[pmid] = (retrieved_ids, data_list)

    pimd_count = {}
    id_counter = 0
    text_data = []
    for p in pimd:
        retrieved_ids, data_list = results.get(p, (0, []))
        pimd_count[p] = (id_counter, id_counter + retrieved_ids)
        id_counter += retrieved_ids
        text_data.extend(data_list)

    matrix = tf_idf_sklearn(text_data)
    clusters = clustering_kmeans(matrix, len(pimd))
    log("Data Similarity matrix", similarity(matrix))
    log("Data Clustering", clusters)
    log("Data", pimd_count)
    plot_clusters(matrix, clusters, pimd_count)


if __name__ == "__main__":
    main(get_arguments())