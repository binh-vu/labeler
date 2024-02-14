import re
from pathlib import Path

import pandas as pd
import serde.csv
import serde.json


def get_location(loc):
    if loc == "" or loc is None:
        return None
    if loc.lower().find("multipoint") != -1:
        m = re.match(
            r"multipoint *\((?P<point>-?\d+(\.\d+)?[ ,]+-?\d+(\.\d+)?)", loc.lower()
        )
        point = m.group("point")
        if "," in point:
            long, lat = point.split(",", 1)
        else:
            long, lat = point.split(" ", 1)
        return long, lat
    longlat = loc.split("(", 1)[1].split(")")[0]
    if longlat.find(",") == -1:
        long, lat = longlat.split(" ", 1)
    else:
        long, lat = longlat.split(",", 1)

    return long, lat


limit = 10000
out = []
for r in serde.json.deser(Path(__file__).parent.parent / f"data_{limit}.json"):
    loc = get_location(r["location"])
    o = {
        "id": r["id"],
        "name": r["label"],
        "country": r["country"],
    }
    if loc is not None:
        o["long"] = loc[0]
        o["lat"] = loc[1]
        out.append(o)

pd.DataFrame(out).to_csv(
    Path(__file__).parent.parent / f"data_{limit}.csv", index=False
)
