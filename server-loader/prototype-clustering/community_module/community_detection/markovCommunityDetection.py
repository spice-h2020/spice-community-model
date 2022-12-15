# Authors: José Ángel Sánchez Martín
import networkx as nx
from networkx.algorithms import community
import markov_clustering as mc
from community_module.community_detection.graphCommunityDetection import GraphCommunityDetection

class MarkovCommunityDetection(GraphCommunityDetection):

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
        list
            List with the clusters each element belongs to (e.g., list[0] === cluster the element 0 belongs to.) 
        """
        self.graph = self.generateGraph(self.data.index,distanceMatrix)
        
        # Get adjacency matrix of graph
        A = nx.to_numpy_matrix(self.graph)

        # Apply Markov Clustering algorithm
        result = mc.run_mcl(A)
        clusters = mc.get_clusters(result)
        
        print("markov clustering")
        print(type(clusters))
        print(n_clusters)
        print(clusters)
        print("fin markov clustering")
        print("\n")

        return clusters
        
      