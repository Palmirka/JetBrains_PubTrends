import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans, DBSCAN

from logs import save


def tf_idf_sklearn(data: list[any]) -> any:
    """
    Usage of tfidf algorithm to vectorizing data

    :param data: list of dictionaries
    :return: tf idf matrix
    """
    print("===================================")
    print(type(data[0]))
    vectorizer = TfidfVectorizer(stop_words="english")
    text_data = [" ".join([text for key, text in item.items() if key != 'pimd']) for item in data]
    tf_idf_matrix = vectorizer.fit_transform(text_data)
    feature_names = vectorizer.get_feature_names_out()
    save((feature_names, tf_idf_matrix.toarray()), "output.csv")
    return tf_idf_matrix


def similarity(tf_idf_matrix) -> np.ndarray:
    """
    Cosine similarity algorithm

    :param tf_idf_matrix:
    :return:
    """
    return cosine_similarity(tf_idf_matrix)


def clustering_kmeans(tf_idf_matrix, clusters_number: int) -> np.ndarray:
    kmeans = KMeans(n_clusters=clusters_number, random_state=42, n_init=10)
    return kmeans.fit_predict(tf_idf_matrix)

def clustering_dbscan(tf_idf_matrix, eps: float = 0.5, min_samples: int = 5) -> np.ndarray:
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    return dbscan.fit_predict(tf_idf_matrix)


def plot_clusters(tfidf_matrix, clusters, pmid_to_dataset) -> None:
    """
    Function responsible for creating visualization of clusters and data

    :param tfidf_matrix:
    :param clusters:
    :param pmid_to_dataset:
    :return:
    """
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(tfidf_matrix.toarray())

    pmid_list = list(pmid_to_dataset.keys())
    colors = plt.cm.get_cmap("tab20", len(pmid_list)) # Kolory dla PMID
    pmid_color_map = {pmid: colors(i) for i, pmid in enumerate(pmid_list)}

    plt.figure(figsize=(20, 14))

    for pmid, (start, end) in pmid_to_dataset.items():
        color = pmid_color_map.get(pmid, "gray")
        xs, ys = [], []

        for idx in range(start, end):
            x, y = reduced[idx]
            xs.append(x)
            ys.append(y)
            cluster = clusters[idx]

            plt.scatter(x, y, color=color, alpha=0.75, edgecolors="black", s=100)
            plt.text(x, y, str(cluster), fontsize=7, ha="center", va="center", color="black", fontweight="bold")

        if len(xs) > 1:
            plt.plot(xs + [xs[0]], ys + [ys[0]], color=color, alpha=0.5, linestyle="--", linewidth=2)

    handles = [plt.Line2D([0], [0], marker='o', color='w',
                          markerfacecolor=pmid_color_map[pmid], markersize=10, label=pmid)
               for pmid in pmid_list]
    plt.legend(handles=handles, title="PMIDs", bbox_to_anchor=(1.05, 1), loc='best')

    plt.xlabel("Component 1")
    plt.ylabel("Component 2")
    plt.title("GEO Dataset Clustering")
    plt.show()