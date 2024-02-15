from pathlib import Path

import serde.json
from rdflib import RDF, BNode, Graph, Literal, Namespace, URIRef
from slugify import slugify

# data = serde.json.deser(Path(__file__).parent.parent / f"data/data_10000.json")


# def get_ann_file(mineral_site_id: str, mineral_site_name: str):
#     assert mineral_site_id.startswith("https://minmod.isi.edu/resource/")
#     id = mineral_site_id[len("https://minmod.isi.edu/resource/") :]

#     ann_file = (
#         Path(__file__).parent.parent
#         / "annotations"
#         / (slugify(mineral_site_name) + "__" + slugify(id) + ".json")
#     )
#     return ann_file


# for row in data:
#     file = get_ann_file(row["id"], row["label"])
#     if file.exists():
#         ann = serde.json.deser(file)
#         if "id" not in ann:
#             ann["id"] = row["id"]
#         serde.json.ser(ann, file)

g = Graph()
MNDR = Namespace("https://minmod.isi.edu/resource/")

for file in (Path(__file__).parent.parent / "annotations").iterdir():
    ann = serde.json.deser(file)
    for val in ann["deposit_types"]:
        if val != "none" and val.startswith("https"):
            dtc = BNode()
            g.add((dtc, RDF.type, MNDR.DepositTypeCandidate))
            g.add((dtc, MNDR.normalized_uri, URIRef(val)))
            g.add((dtc, MNDR.confidence, Literal(1.0)))
            g.add((dtc, MNDR.source, Literal("expert")))

            g.add((URIRef(ann["id"]), MNDR.deposit_type_candidate, dtc))

g.serialize(
    Path(__file__).parent.parent / f"data/ann_35_mines_20240214.ttl", format="turtle"
)
