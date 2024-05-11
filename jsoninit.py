import json

file = open("input.txt", "+r")
data = []
while(True):
    line = file.readline()
    if(line == ''):
        break
    elif(line=="\n"):
        continue
    else:
        data.append(line.strip())

json_fp = open("nasdaq.json", "w")
json_data = {
    "data": data
}
json.dump(json_data, json_fp, indent=4)
print(data)