"""The purpose of this app is to annotate/curate deposit types of mineral site data.
"""

# %%
import pandas as pd
from collections import defaultdict
from functools import partial
from pathlib import Path

import serde.json
import streamlit as st
import streamlit.components.v1 as components
from slugify import slugify

from labeler.misc import percentage, run_minmod_query

# %%


@st.cache_data
def get_data(limit: int = 100):
    return serde.json.deser(Path(__file__).parent.parent / f"data/data_{limit}.json")
    df = run_minmod_query(
        """
SELECT (?ms as ?mineral_site_id) (?msl as ?mineral_site_label) ?coor ?crs ?country ?dtc ?dtc_name ?dtc_confidence ?dtc_source ?dtc_uri
WHERE {
    ?ms a :MineralSite ;
        rdfs:label ?msl ;
        :location_info ?loc .

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
        ?dtc :normalize_uri ?dtc_uri .
    }

    FILTER (?country = "United States" || ?country = "USA")
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
                "deposit_types": defaultdict(list),
            }

        dtc_name = row.get("dtc_name", "")
        source = row.get("dtc_source", "")

        if source == "":
            continue

        out[row["mineral_site_id"]]["deposit_types"][source].append(
            {
                "id": row.get("dtc", f'{row["mineral_site_id"]}/{dtc_name}/{source}'),
                "normed_uri": row.get("dtc_uri", ""),
                "name": row.get("dtc_name", ""),
                "confidence": float(row["dtc_confidence"]),
                "source": row.get("dtc_source", ""),
            }
        )
        out[row["mineral_site_id"]]["deposit_types"][source].sort(
            key=lambda x: x["confidence"], reverse=True
        )

    return list(out.values())


@st.cache_data
def get_deposit_types():
    return pd.read_csv(Path(__file__).parent.parent / "data/deposit_types.csv")


def get_ann_file(mineral_site_id: str, mineral_site_name: str):
    assert mineral_site_id.startswith("https://minmod.isi.edu/resource/")
    id = mineral_site_id[len("https://minmod.isi.edu/resource/") :]

    ann_file = (
        Path(__file__).parent.parent
        / "annotations"
        / (slugify(mineral_site_name) + "__" + slugify(id) + ".json")
    )
    return ann_file


def get_annotation(mineral_site_id: str, mineral_site_name: str):
    ann_file = get_ann_file(mineral_site_id, mineral_site_name)
    if ann_file.exists():
        return serde.json.deser(ann_file)
    return None


def save_deposit_type(
    mineral_site_id: str,
    mineral_site_name: str,
    deposit_type: str,
):
    ann = get_annotation(mineral_site_id, mineral_site_name)
    if ann is None:
        ann = {
            "id": mineral_site_id,
            "deposit_types": [deposit_type],
        }
    else:
        if deposit_type in ann["deposit_types"]:
            ann["deposit_types"].remove(deposit_type)
        else:
            ann["deposit_types"].append(deposit_type)
    serde.json.ser(ann, get_ann_file(mineral_site_id, mineral_site_name))


# %%

st.set_page_config(layout="wide")
default_limit = 10000

queryparams = st.query_params.to_dict()
if "limit" not in queryparams:
    st.query_params["limit"] = default_limit
if not st.query_params["limit"].isdigit():
    st.query_params["limit"] = default_limit

if "start" not in queryparams:
    st.query_params["start"] = 0
if not st.query_params["start"].isdigit():
    st.query_params["start"] = 0

limit = int(st.query_params["limit"])
df = get_data(limit)


def set_start(start: int):
    if start < 0:
        start = 0
    if start < len(df):
        st.query_params["start"] = start


start = int(st.query_params["start"])
if start >= len(df) or start < 0:
    st.query_params["start"] = 0
    start = 0

st.header("Annotate Deposit Types")
st.write(
    "The purpose of this app is to annotate/curate deposit types of mineral site data."
)
st.write(
    "For now, we are annotating Magmatic Nickel deposit types. Please see verify the list of Magmatic Nickel below if they are complete."
)

st.subheader("Magmatic Nickel Deposit Types")
st.write(get_deposit_types())


header1, header2 = st.columns(2)
with header1:
    st.subheader(f"Annotator")
with header2:
    cc1, cc2, cc3 = st.columns([2, 1, 1])
    with cc1:
        st.write(f"**Progress {percentage(start, len(df))}**")
    with cc2:
        st.button("Previous", on_click=lambda: set_start(start - 1))
    with cc3:
        st.button("Next", on_click=lambda: set_start(start + 1))

deposit_types = get_deposit_types()


def get_location(loc):
    if loc == "" or loc is None:
        return None
    longlat = loc.split("(", 1)[1].split(")")[0]
    if longlat.find(",") == -1:
        long, lat = longlat.split(" ", 1)
    else:
        long, lat = longlat.split(",", 1)

    return long, lat


def display_example(site):
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Mineral Site:** [{site['label']}]({site['id']})")
        st.write("**Country:** " + site.get("country", ""))

        st.write("**Candidate Deposit Type:**")
        cols = st.columns(len(site["deposit_types"]))
        for i, (source, dtcs) in enumerate(site["deposit_types"].items()):
            with cols[i]:
                st.write(f"**Source:** {source}")
                for dtc in dtcs:
                    st.write(f"  - {dtc['name']}: {dtc['confidence']:.2f}")

    with col2:
        site_location = get_location(site["location"])
        if site_location is not None:
            long, lat = site_location
            marker = f"{lat}%2C{long}"
            components.html(
                f"""
            
    <iframe 
        width="720" 
        height="400" 
        src="https://www.openstreetmap.org/export/embed.html?bbox=-117.24609375000001%2C34.66935854524545%2C-77.16796875000001%2C58.35563036280967&amp;layer=mapnik&amp;marker={marker}" style="border: 1px solid black">
    </iframe><br/><small><a href="https://www.openstreetmap.org/?mlat=47.843&amp;mlon=-97.207#map=5/47.843/-97.207">View Larger Map</a></small>
            
            """,
                height=400,
            )
        else:
            st.write("No location information available")
    st.write("**Normalized Deposit Types:**")

    site_annotation = get_annotation(site["id"], site["label"])
    if site_annotation is None:
        site_annotation = {"deposit_types": []}

    cols = st.columns(4)
    for ri, (_, dtc) in enumerate(deposit_types.iterrows()):
        with cols[ri % len(cols)]:
            selected = dtc["id"] in site_annotation["deposit_types"]

            st.button(
                dtc["name"],
                type="primary" if selected else "secondary",
                on_click=partial(
                    save_deposit_type, site["id"], site["label"], dtc["id"]
                ),
            )

    with cols[len(deposit_types) % len(cols)]:
        selected = "none" in site_annotation["deposit_types"]
        st.button(
            "none",
            type="primary" if selected else "secondary",
            on_click=partial(save_deposit_type, site["id"], site["label"], "none"),
        )


display_example(df[start])
