# Authors: José Ángel Sánchez Martín
from sklearn_extra.cluster import KMedoids

class KmedoidsCommunityDetection:

    def __init__(self, data):
        """Construct of SimilariyCommunityDetection objects.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of attributes names and
            values contain the attribute values for each element.
        """
        self.data = data

    def calculate_communities(self, distanceMatrix='euclidean', n_clusters=2):
        """Method to calculate the communities of elements from data.

        Parameters
        ----------
        distanceMatrix : np.ndarray
            Square matrix encoding the distance between datapoints
        n_clusters : int, optional
            Number of clusters (communities) to search, by default 2

        Returns
        -------
        dict
            Dictionary with all elements and its corresponding community.
        """
        kmedoids = KMedoids(metric='precomputed',method='pam', n_clusters=n_clusters, init='k-medoids++')
        kmedoids.fit(distanceMatrix)
        
        return kmedoids.labels_