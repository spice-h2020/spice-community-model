from fcmeans import FCM

class FuzzyCMeansCommunityDetection:

    def __init__(self, data):
        """Construct of opticsCommunityDetection.

        Parameters
        ----------
        data : pd.DataFrame
            Dataframe where index is ids of elements, columns a list of attributes names and
            values contain the attribute values for each element.
        """
        self.data = data

    def calculate_communities(self, distanceMatrix, n_clusters=2):
        """
        Method to calculate the communities of elements from data.

        Parameters
        ----------
        metric :
            distanceMatrix
        n_clusters : int, optional
            The number of clusters to form as well as the number
        max_iter : int, optional
            Maximum number of iterations of the fuzzy C-means
        m : float, optional
            Degree of fuzziness
        error : float, optional
            Relative tolerance with regards to Frobenius norm of

        Returns
        -------
        list
            List with the clusters each element belongs to (e.g., list[0] === cluster the element 0 belongs to.) 
        """
        # devuelve resultados incorrectos, si se pide 3 n_cluster y solo encuentra 2 devuelve [1,2,2,1] pero tiene que devolver [0,1,1,0]
        # TODO: fix
        
        # fcm = FCM(n_clusters=n_clusters)
        # print("1", fcm.fit(distanceMatrix))
        # clusters = fcm.predict(distanceMatrix)
        # print("clusters:", clusters)

        size = max(len(distanceMatrix), len(distanceMatrix[0]))
        communities = [0] * size


        return communities
