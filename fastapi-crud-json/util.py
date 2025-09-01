# train rasa with the specified data inside Input Folder
import json


def validate_data(text, intent, entities_list):
    final_text = text
    final_intent = intent
    # start =  end = entity = value = []
    obj_dict = {}

    list_dict = []
    for data in entities_list:
        entity = data['entity']
        value = data['value']
        start = data['start']
        end = data['end']
        list_dict.append({"start": start,
                          "end": end,
                          "value": value,
                          "entity": entity})
    temp = {"text": final_text,
            "intent": final_intent,
            "entities": list_dict}
    obj_dict.update(temp)

    return obj_dict


def add_json(k, v):
    file = open('static/test.json', 'r+', encoding="utf8")
    # Move the file pointer to the beginning
    file.seek(0)
    json_data = json.load(file)

    # Add new data to the existing JSON
    final_data = {
        "rasa_nlu_data": {
            "common_examples": [
                {
                    "text": k,
                    "intent": v,
                    "entities": []
                }
            ]
        }
    }
    json_data["rasa_nlu_data"]["common_examples"].extend(final_data["rasa_nlu_data"]["common_examples"])

    # Move the file pointer to the beginning to overwrite the file
    file.seek(0)

    # Write the updated JSON data
    json.dump(json_data, file, indent=4)

    # Truncate the remaining content after the updated JSON data
    file.truncate()
    file.close()


def read_json():
    try:
        with open('static/test.json', 'r', encoding="utf-8-sig") as f:
            json_data = json.load(f)

        intends = set()
        nlu_dict = {}
        for i in json_data['rasa_nlu_data']['common_examples']:
            text = i['text']
            intent = i['intent']
            intends.add(intent)
            nlu_dict[text] = intent

        return nlu_dict, intends

    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("An error occurred while processing the JSON file:", e)
        return None, None


# read_json()
def remove_json(k, v=""):
    try:
        with open('./static/test.json', 'r', encoding="utf-8") as file:
            json_data = json.load(file)
        
        final_data = {
            "text": k,
            "intent": v,
            "entities": []
        }
        
        # Remove the entry from the JSON data
        common_examples = json_data["rasa_nlu_data"]["common_examples"]
        common_examples = [example for example in common_examples if example["text"] != final_data["text"]]
        json_data["rasa_nlu_data"]["common_examples"] = common_examples
        
        with open('./static/test.json', 'w', encoding="utf-8") as file:
            json.dump(json_data, file, indent=4)
            
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print("An error occurred while processing the JSON file:", e)

def update_json(text, intent=""):
    with open('./static/test.json', 'r+', encoding="utf8") as fp:
        # Move the file pointer to the beginning
        fp.seek(0)
        json_data = json.load(fp)
        common_examples = json_data["rasa_nlu_data"]["common_examples"]
        for example in common_examples:
            if example["text"] == text:
                example['intent'] = intent

        fp.seek(0)
        fp.truncate()
        json.dump(json_data, fp, indent=4)
