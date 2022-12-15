# Prototype Clustering Techniques

This repository contains several prototypes that use different similarity metrics and clustering techniques on different SPICE case studies.

## Examples

- **Example 1**: This example shows how to implement community detection based on the similarity between a property of users. In addition, this example shows how to apply a custom similarity measure to detect communities. This code detects up to 5 communities based on the emotions that
users felt watching artworks (information saved in users_emotions.json).

- **Example 2**: This example shows how to implement community detection based on the similarity between a property of users. In addition, this example shows how to apply a basic similarity measure to detect communities. Basic similarity metrics are detailed in class SimilarityCommunityDetection. This code detects up to 5 communities based on the emotions that users felt watching artworks (information saved in users_emotions.json).

- **Example 3**: This example shows how to implement community detection using graphs to relate users. In this example, it is possible to apply  *Markov Clustering* and *Greedy Modularity* algorithms. Data used in this example is emotions_graphs.json.

Usage:
- Execute Docker from `community-model-api`
- Execute `api_server/api_server.py`

Requierements:
- Solo usar el `requierements.txt`

El fichero `requierements_conda.txt` es obsoleto y hay que actualizarlo, es para el CM