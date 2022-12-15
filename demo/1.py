

import requests
import json

def main():

    data =  [
  {
    "id": "6331fe3bda21134eb64f7700",
    "userid": "fqybaAk8",
    "origin": "35450",
    "source_id": "fake90e6d701748f08514b01",
    "source": "fake",
    "pname": "itMakesMeFeel.text",
    "pvalue": "",
    "context": "application",
    "datapoints": 0,
    "category": "interest"
  },
  {
    "id": "6331fe3bda21134eb64f7700",
    "userid": "fqybaAk8",
    "origin": "35287",
    "source_id": "fake90e6d701748f08514b01",
    "source": "fake",
    "pname": "itMakesMeFeel.text",
    "pvalue": "triste perch\u00e9 mi ricordo la storia della Monaca",
    "context": "application",
    "datapoints": 0,
    "category": "interest"
  }
]

    # api = DAO_api()

    a = requests.post("http://localhost:8080/v1.1/users/fqybaAk8/update-generated-content", json = data)
    print(a)
    print(a.text)


main()