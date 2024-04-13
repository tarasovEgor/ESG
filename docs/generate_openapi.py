#!/usr/bin/python

import requests
import pandas as pd

api = requests.get("https://ai-service.ethics-hse.ru/openapi.json").json()

types = {}
for schema_name, schema_val in api["components"]["schemas"].items():
    if schema_val.get("properties", None) is None:
        continue
    types[schema_name] = []
    for type_name, type_val in schema_val["properties"].items():
        res = [type_name, type_val["type"]]
        if type_val["type"] == "array":
            if type_val["items"].get("$ref", None) is not None:
                res.append(type_val["items"]["$ref"].split("/")[-1])
            elif type_val["items"].get("type", None) is not None:
                res[1] = f"array[{type_val['items']['type']}]"
        types[schema_name].append(res)

for type_name, sub_types in types.items():
    for params in sub_types:
        if len(params) == 3:
            s = (
                "[{\n\t"
                + "\n\t".join([f"{type_name}: {type_type}" for (type_name, type_type) in types[params[2]]])
                + "\n}]"
            )
            params[1] = s
            del params[2]

for type_name, sub_types in types.items():
    types[type_name] = (
        "{\n\t" + "\n\t".join([f"{type_name}: {type_type}" for (type_name, type_type) in sub_types]) + "\n}"
    )


routes = {}
for path, val in api["paths"].items():
    for method_type, data in val.items():
        path_method = f"{method_type.upper()}\\par{path}"
        routes[path_method] = {}
        p = []
        if data.get("parameters") is not None:
            parameters = data["parameters"]
            for param in parameters:
                p.append([param["name"], param["schema"].get("type", None)])
        routes[path_method]["parameters"] = "\n".join([f"{name}: {type_}" for (name, type_) in p])
        routes[path_method]["body"] = None
        if data.get("requestBody") is not None:
            routes[path_method]["body"] = types.get(
                data["requestBody"]["content"]["application/json"]["schema"]["$ref"].split("/")[-1]
            )
        response = data["responses"].get("200")
        if response or response["content"]["application/json"]["schema"].get("$ref"):
            response = types.get(response["content"]["application/json"]["schema"].get("$ref", "").split("/")[-1])
        else:
            response = "str"
        routes[path_method]["response"] = response

df = pd.DataFrame(routes).T.fillna("").reset_index()

s = ""
for _, row in df.iterrows():
    s += "\n" + row[0] + "".join(["&" + item for item in row[1:]]) + "\\\\"
s = s.replace("_", "\\_").replace("\n", "\\par\n").replace("{", "\\{").replace("}", "\\}")
s = (
    "\\begin{longtblr}[caption={Запросы API\\label{tbl:api_doc} }]{colspec={|X[l]|X[l]|X[l]|X[l]|},rowhead = 1,hlines}\n"
    + "\\textbf{Путь}&\\textbf{Параметры запроса}&\\textbf{Тело запроса}&\\textbf{Результат запроса}\\\\"
    + s
    + "\n\\end{longtblr}"
)
with open("api_table.tex", "w") as f:
    f.write(s)
