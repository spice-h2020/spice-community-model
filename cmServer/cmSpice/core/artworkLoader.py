import json
import pandas as pd
import re


class artworkLoader():

    def __init__(self, type, url=None):
        self.type = type
        self.url = url
        self.seedFile = None
        self.artworks = None

        f = open('seed.json')
        self.seedFile = json.load(f)

        self.__readArtworks()
        if not self.__checkUsingSeedFile():
            self.__transform()

    def __readArtworks(self):

        if self.url is None:
            f = open('localFIle.json')
            self.artworks = json.load(f)
        else:
            f = open('apiFile.json')
            self.artworks = json.load(f)

    def __checkUsingSeedFile(self):
        for att in self.seedFile["artwork_attributes"]:
            for artwork in self.artworks:
                if att["on_attribute"]["att_name"] not in artwork:
                    # print(att["on_attribute"]["att_name"])
                    return False
        return True

    def __transform(self):
        artifacts = pd.DataFrame(self.artworks)

        artifacts['Materials'] = artifacts.apply(lambda row: self.__transformMaterial(row), axis=1)

        if self.type == "GAM":
            artifacts['ApproxYear'] = artifacts['Year'].apply(self.__convertToYear)
            artifacts['ApproxYear'].fillna(value=0, inplace=True)
            artifacts['Decade'] = artifacts['ApproxYear'].apply(lambda v: int((v - 1) / 10) * 10)

        self.artworks = artifacts.to_json(orient='records')

    def __transformMaterial(self, row):
        """Returns a list of materials according to a dictionary for transformations
        It looks up the value of the 'Material_ and_echnique' columns and tries to transform it
        If no material is detected then it returns an empty list
        """
        if self.type == "GAM":
            materialTransformer = {
                "SU TELA": "canvas",
                "BRONZO": "bronze",
                "MARMO": "marble",
                "COMPENSATO": "plywood",
                "LEGNO": "wood",
                "TAVOLA": "wood",
                "CERAMICA": "ceramics",
                "CARTA": "paper",
                "CARTONE": "paper"
            }
            value = [] if "none" in row['Materials'] else row['Materials'].replace(" ", "").split(',')
            for key, val in materialTransformer.items():
                if key in row['Material_ and_echnique'].strip().upper():
                    value.append(val)
            return value
        elif self.type == "DMH":
            value = [] if "none" in row['Materials'] else row['Materials'].replace(" ", "").split(',')
            return value

    def __convertToYear(self, date):
        date = str(date)
        # leave only words, years and ranges
        date = "".join(date.split(" /"))
        # 1. Find ranges
        ranges = re.findall("([12][0-9]{3})-([12][0-9]{3})", date)
        if ranges:
            numRanges = []
            for r in ranges:
                y1 = int(r[0])
                y2 = int(r[1])
                # Ranges are simplified to the middle value
                numRanges.append(int((y1 + y2) / 2))
            return int(sum(numRanges) / len(numRanges))
        else:
            # 2. If we find several years, we try to compute the middle value among them
            years = re.findall("([12][0-9]{3})", date)
            if years:
                numYears = [int(y) for y in years]
                return int(sum(numYears) / len(numYears))
            else:
                return None

    def getArtworks(self):

        return self.artworks
