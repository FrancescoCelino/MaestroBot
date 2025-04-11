import json

with open('gozomaxxing json/result.json', 'r') as input_file:
    data = json.load(input_file)

with open('maestro_gozomaxxing.txt', 'w') as output_file:
    output_file.write('')


#print(data)             # Print the entire JSON content
#print(data.keys())    # stampa i campi del primo livello name, type, id, messages 


lines_added = 0

with open('maestro_gozomaxxing.txt', 'w') as output_file:
    for message in data['messages']:
        if 'text' in message:
            if 'from_id' in message:
                if message['from_id']=='user357010412':
                    if type(message['text'])==str:
                        output_file.write(message['text']+"\n")
                        #print(message['text'], '\n')
                        lines_added += 1

    print(f"Added {lines_added} lines to maestro_gozomaxxing.txt")