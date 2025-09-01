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
    file = open('./input/data.json', 'r+', encoding="utf8")
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
    with open('./input/data.json', 'r', encoding="utf8") as f:
        json_data = json.load(f)

    final_data = {"rasa_nlu_data": {
        "common_examples": [
        ]
    }}
    # entities_set = set()
    intends = set()
    question = set()
    # synonyms = set()
    nlu_dict = {}
    for i in json_data['rasa_nlu_data']['common_examples']:
        text = i['text']
        question.add(text)
        intent = i['intent']
        intends.add(intent)
        entities_list = i['entities']
        nlu_dict[text] = intent
        # for entity in entities_list:
        #     entities_set.add(tuple({entity[entity]: entity['value']}))
        # entities_set.add(tuple({entities_list[0]['entity']: entities_list[0]['value']}))
        temp_dict = validate_data(text, intent, entities_list)
        final_data['rasa_nlu_data']['common_examples'].append(temp_dict)
        # print(entities_list[0]['value'])
    # print(intends, '--> intent')
    # print(entities_set, " --> entity")
    # file = open('../input/final_data.json', 'w', encoding="utf8")
    # file.write(json.dumps(final_data))
    # file.close()
    return nlu_dict, intends


# read_json()

def remove_json(k, v=""):
    file = open('./input/data.json', 'r+', encoding="utf8")
    # Move the file pointer to the beginning
    file.seek(0)
    json_data = json.load(file)
    final_data = {

        "text": k,
        "intent": v,
        "entities": []

    }
    # print(final_data)
    # common_examples = json_data["rasa_nlu_data"]["common_examples"]
    # for example in common_examples:
    #     # print(example["text"])
    #     if example["text"] == final_data["text"]:
    #         print("yes")
    # Remove the entry from the JSON data
    common_examples = json_data["rasa_nlu_data"]["common_examples"]
    common_examples = [example for example in common_examples if example["text"] != final_data["text"]]
    json_data["rasa_nlu_data"]["common_examples"] = common_examples
    file.seek(0)
    json.dump(json_data, file, indent=4)
    file.truncate()

    file.close()


def print_pipeline(pipeline):
    result = []
    for key, value in pipeline.items():
        result.append(f"{key}:")
        if isinstance(value, list):
            for item in value:
                for sub_key, sub_value in item.items():
                    result.append("\t" + sub_key + ": " + str(sub_value) + '\n')
        else:
            result.append("\t" + str(value) + '\n')
    return "\n".join(result)
