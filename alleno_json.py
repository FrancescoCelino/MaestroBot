import json

with open('gozomaxxing json/result.json', 'r') as file:
    data = json.load(file)

#print(data)             # Print the entire JSON content
print(data.keys())    # stampa i campi del primo livello

# visito i campi annidati del campo messages
for i, message in enumerate (data['messages']):
    if i >= 200:
        break
    if 'text' in message:
        print(message['text'])
    else:
        print("No text found in this message.")