from typing import Callable, Optional, Union

import pandas as pd
import requests


def run_sparql_query(query, endpoint="https://minmod.isi.edu/sparql", values=False):
    # add prefixes
    final_query = (
        """
    PREFIX dcterms: <http://purl.org/dc/terms/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX : <https://minmod.isi.edu/resource/>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX gkbi: <https://geokb.wikibase.cloud/entity/>
    PREFIX gkbp: <https://geokb.wikibase.cloud/wiki/Property:>
    PREFIX gkbt: <https://geokb.wikibase.cloud/prop/direct/>
    PREFIX geo: <http://www.opengis.net/ont/geosparql#>
    \n"""
        + query
    )
    # send query
    response = requests.post(
        url=endpoint,
        data={"query": final_query},
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/sparql-results+json",  # Requesting JSON format
        },
        verify=False,  # Set to False to bypass SSL verification as per the '-k' in curl
    )
    # print(response.text)
    try:
        qres = response.json()
        if "results" in qres and "bindings" in qres["results"]:
            df = pd.json_normalize(qres["results"]["bindings"])
            if values:
                filtered_columns = df.filter(like=".value").columns
                df = df[filtered_columns]
                df.rename(
                    columns={
                        col: col.replace(".value", "") for col in filtered_columns
                    },
                    inplace=True,
                )
            return df
    except:
        raise


def run_minmod_query(query, values=False):
    return run_sparql_query(
        query, endpoint="https://minmod.isi.edu/sparql", values=values
    )


def percentage(
    a: Union[float, int],
    b: Union[float, int],
    format: Optional[Callable[[Union[float, int]], str]] = None,
) -> str:
    if format is None:
        return "%.2f%% (%d/%d)" % (a * 100 / b, a, b)
    return "%.2f%% (%s/%s)" % (a * 100 / b, format(a), format(b))
