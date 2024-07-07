import json


def load_json(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

# Функция для сохранения данных в JSON файл
def save_json(data, file_path):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

data = load_json("htmls.json")
cc = set()
finalData =[]
print(len(data))
for t in data:
    if t["html"] not in cc:
        cc.add(t["html"])
        finalData.append(t)
print(len(cc))
print(len(finalData))

print(finalData[2])

save_json(finalData, "html.json")