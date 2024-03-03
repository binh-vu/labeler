# %%

from collections import defaultdict
from functools import partial
from pathlib import Path

import pandas as pd
import serde.json
import streamlit as st
import streamlit.components.v1 as components
from slugify import slugify

from labeler.misc import percentage, run_minmod_query

# %%

run_minmod_query(
    """
SELECT ?id ?label ?environment ?group
WHERE {
<https://minmod.isi.edu/resource/Q478> a :DepositType ;
    rdfs:label ?label ;
                 :environment ?environment ;
                :deposit_group ?group .
}
                 """
)

# %%


run_minmod_query(
    """
SELECT ?id ?environment ?group ?name
WHERE {
    ?id 
                 :environment ?environment ;
    :deposit_group ?group ;
    rdfs:label ?name .

VALUES ?id { :Q478 }
                            }
                 """
)
# %%


run_minmod_query(
    """
SELECT ?id ?environment ?group ?name
WHERE {
    ?id rdfs:label ?name ;
    :environment ?environment ;
                                :deposit_group ?group .
                            
                            VALUES ?id { :Q478 }
                            }
                 """
)
# %%

run_minmod_query(
    """
SELECT *
WHERE {
    ?s :record_id 10067592 ;
                 :deposit_type_candidate [ ?p ?o ] .
}
                 LIMIT 1000
"""
)
# %%


run_minmod_query(
    """
SELECT ?ms ?oms ?dt_conf ?dt_s ?cn ?cg ?ce ?country ?dtnorm ?dtnorm_label ?loc_wkt
WHERE {
    ?ms a :MineralSite .
    ?ms :deposit_type_candidate ?dpc .
    ?dpc :confidence ?dt_conf .
    ?dpc :source ?dt_s .
    
    OPTIONAL { ?ms owl:sameAs ?oms . }

    ?dpc :normalized_uri ?dtnorm .
    ?dtnorm rdfs:label ?dtnorm_label .
    ?ms :location_info [ :country ?country ] .

    OPTIONAL {
        ?ms :location_info [ :location ?loc_wkt ] .
        FILTER(datatype(?loc_wkt) = geo:wktLiteral)
    }
}"""
)

# %%

df = run_minmod_query(
    """
SELECT DISTINCT ?ms ?msname # ?cat ?ore
WHERE {
    ?ms a :MineralSite ;
        rdfs:label|:name ?msname .
    ?ms :deposit_type_candidate ?dpc .

    ?ms :mineral_inventory ?mi .

    ?mi :ore [ :ore_value ?ore ] ;
        :category ?cat .

    ?dpc :confidence ?dt_conf .
    ?dpc :source 'expert' .
    
    # OPTIONAL { ?ms owl:sameAs ?oms . }

    # ?dpc :normalized_uri ?dtnorm .
    # ?dtnorm rdfs:label ?dtnorm_label .
    # ?ms :location_info [ :country ?country ] .

    # OPTIONAL {
    #     ?ms :location_info [ :location ?loc_wkt ] .
    #     FILTER(datatype(?loc_wkt) = geo:wktLiteral)
    # }
}"""
)

# %%

uris = set(df["ms.value"].unique())

# %%

df3 = pd.read_csv("/Users/rook/Downloads/flat_mineral_site_data.v3.csv")
df2 = pd.read_csv("/Users/rook/Downloads/filtered_nickel_us.0216.csv")
# %%


run_minmod_query(
    """
SELECT ?ms ?msname
WHERE {
    ?ms a :MineralSite ;
        rdfs:label ?msname .
    ?ms :deposit_type_candidate ?dpc .
    ?dpc :confidence ?dt_conf .
    ?dpc :source 'expert' .
    
    # OPTIONAL { ?ms owl:sameAs ?oms . }

    # ?dpc :normalized_uri ?dtnorm .
    # ?dtnorm rdfs:label ?dtnorm_label .
    # ?ms :location_info [ :country ?country ] .

    # OPTIONAL {
    #     ?ms :location_info [ :location ?loc_wkt ] .
    #     FILTER(datatype(?loc_wkt) = geo:wktLiteral)
    # }
}"""
)
