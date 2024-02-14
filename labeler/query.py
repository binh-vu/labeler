# %%

from collections import defaultdict
from functools import partial
from pathlib import Path

import serde.json
import streamlit as st
import streamlit.components.v1 as components
from slugify import slugify

from labeler.misc import percentage, run_minmod_query

# %%

run_minmod_query("""
SELECT ?id ?label
WHERE {
:Q478 a :DepositType ;
    rdfs:label ?label .
}
                 """)

# %%


run_minmod_query("""
SELECT ?id ?environment ?group ?name
WHERE {
    ?id 
                 :environment ?environment ;
    :deposit_group ?group ;
    rdfs:label ?name .

VALUES ?id { :Q478 }
                            }
                 """)