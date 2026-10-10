from app.tools import run_tool

print("1) get_schema")
print(run_tool("get_schema", {"file_name": "sales.csv"}), "\n")

print("2) revenue by product (top 3)")
print(run_tool("query_data", {
    "file_name": "sales.csv",
    "group_by": ["product"],
    "aggregations": [{"column": "revenue", "function": "sum"}],
    "sort_by": "revenue_sum",
    "limit": 3,
}), "\n")

print("3) filter + total: revenue in the North region")
print(run_tool("query_data", {
    "file_name": "sales.csv",
    "filters": [{"column": "region", "op": "==", "value": "North"}],
    "aggregations": [{"column": "revenue", "function": "sum"}],
}), "\n")

print("4) chart: monthly revenue")
print(run_tool("make_chart", {
    "file_name": "sales.csv", "chart_type": "line", "x": "month", "y": "revenue",
}), "\n")

print("5) a mistake (wrong column): the error goes back as text")
print(run_tool("query_data", {
    "file_name": "sales.csv",
    "group_by": ["country"],
    "aggregations": [{"column": "revenue", "function": "sum"}],
}))
