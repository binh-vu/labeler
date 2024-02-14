"""The purpose of this app is to annotate/curate deposit types of mineral site data.
"""

# %%

from collections import defaultdict
from functools import partial
from pathlib import Path

import serde.json
import streamlit as st
import streamlit.components.v1 as components
from slugify import slugify

from labeler.misc import percentage, run_minmod_query


def get_data(limit: int = 100):
    df = run_minmod_query(
        """
SELECT (?ms as ?mineral_site_id) (?msl as ?mineral_site_label) ?coor ?crs ?country ?dtc ?dtc_name ?dtc_confidence ?dtc_source ?dtc_uri
WHERE {
    ?ms a :MineralSite ;
        :name ?msl ;
        :location_info ?loc ;
        :mineral_inventory [
            :commodity :Q578
        ].

    OPTIONAL { ?loc :location ?coor . }
    OPTIONAL { ?loc :crs ?crs . }
    OPTIONAL { ?loc :country ?country . }

    OPTIONAL { ?ms :deposit_type_candidate ?dtc . }
    OPTIONAL { 
        ?dtc :observed_name ?dtc_name ;
            :confidence ?dtc_confidence ;
            :source ?dtc_source .
    }
    OPTIONAL {
        ?dtc :normalized_uri ?dtc_uri .
    }

    FILTER (?country = "United States" || ?country = "USA" || ?country = "United States of America")
    FILTER (?dtc_source = "sand" || ?dtc_source = "SME")
}
                 """
        + "LIMIT "
        + str(limit),
        values=True,
    )
    assert df is not None
    out = {}
    for ri, row in df.iterrows():
        if row["mineral_site_id"] not in out:
            out[row["mineral_site_id"]] = {
                "id": row["mineral_site_id"],
                "label": row["mineral_site_label"],
                "country": row.get("country", ""),
                "location": row.get("coor", ""),
                "deposit_types": defaultdict(dict),
            }

        dtc_name = row.get("dtc_name", "")
        source = row.get("dtc_source", "")

        if source == "":
            continue

        dtc_record = {
            "id": row.get("dtc", f'{row["mineral_site_id"]}/{dtc_name}/{source}'),
            "normed_uri": row.get("dtc_uri", ""),
            "name": row.get("dtc_name", ""),
            "confidence": float(row["dtc_confidence"]),
            "source": row.get("dtc_source", ""),
        }
        out[row["mineral_site_id"]]["deposit_types"][source][
            dtc_record["name"]
        ] = dtc_record

    for row in out.values():
        for source in row["deposit_types"]:
            row["deposit_types"][source] = sorted(
                row["deposit_types"][source].values(),
                key=lambda x: x["confidence"],
                reverse=True,
            )
    # out[row["mineral_site_id"]]["deposit_types"][source] = sorted(
    #         out[row["mineral_site_id"]]["deposit_types"][source].values(),
    #         key=lambda x: x["confidence"],
    #         reverse=True,
    #     )

    print("limit: ", limit, len(df))
    return list(out.values())



def get_deposit_types():
    deposit_types = [
        f"https://minmod.isi.edu/resource/{x}"
        for x in ["Q478", "Q481", "Q482", "Q486", "Q488", "Q489"]
    ]
    df = run_minmod_query(
        """
        SELECT ?id ?environment ?group ?name
                            WHERE {
                            ?id rdfs:label ?name .
                                # :environment ?environment ;
                                # :deposit_group ?group .
                            
                            VALUES ?id { %s }
                            }
                    
"""
        % " ".join([f"<{x}>" for x in deposit_types]),
        values=True,
    )
    assert df is not None
    return df


DATA_DIR = Path(__file__).parent.parent / "data"
get_deposit_types().to_csv(DATA_DIR / "deposit_types.csv", index=False)

# serde.json.ser(
#     get_data(100), Path(__file__).parent.parent / f"data_{100}.json", indent=2
# )
# serde.json.ser(
#     get_data(10000), Path(__file__).parent.parent / f"data_{10000}.json", indent=2
# )
