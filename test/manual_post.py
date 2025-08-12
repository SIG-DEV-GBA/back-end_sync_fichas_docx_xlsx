import requests

url = "http://localhost:8001/sync/process"
with open("samples/ficha.docx", "rb") as f1, open("samples/anexo.xlsx", "rb") as f2:
    files = {
        "docx": ("ficha.docx", f1, "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        "excel": ("anexo.xlsx", f2, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    }
    r = requests.post(url, files=files, headers={"Accept": "application/json"})
    print(r.status_code, r.text)
