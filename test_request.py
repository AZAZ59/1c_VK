import json
import time
from pprint import pprint

import requests

# act=load_items&al=1&group_id=192858688&hash=dc5f24945c0b68ff2b
from config import group_id, remixsid
from utils import get_id, get_request


def main():
    for k in range(15, 50):
        prop_resp = get_request('[{"action":"addProperty","title":"' + f'prop: {k}' + '","type":"text"}]')
        prop_id = get_id(prop_resp)
        for i in range(1, 150):
            action = '[{"action": "addVariant", "property_id": ' + str(
                    int(prop_id)) + ', "title": "' + f'item {i}' + '"}]'
            resp_json = get_request(action)
            item_id = get_id(resp_json)
            print(f'prop: {k}; item: {i}')
            if item_id == 0:
                break
            time.sleep(0.3)
        print('=' * 120)
        # [{"action":"addProperty","title":"New_Prop","type":"text"}]
        # [{"action":"addVariant","property_id":33,"title":"1"}]
        # Удалить много [{"action":"deleteProperty","property_id":42},{"action":"deleteProperty","property_id":43},{"action":"deleteProperty","property_id":44},{"action":"deleteProperty","property_id":45},{"action":"deleteProperty","property_id":46},{"action":"deleteProperty","property_id":47},{"action":"deleteProperty","property_id":48},{"action":"deleteProperty","property_id":49},{"action":"deleteProperty","property_id":50},{"action":"deleteProperty","property_id":51},{"action":"deleteProperty","property_id":52},{"action":"deleteProperty","property_id":53},{"action":"deleteProperty","property_id":54},{"action":"deleteProperty","property_id":55},{"action":"deleteProperty","property_id":57},{"action":"deleteProperty","property_id":58},{"action":"deleteProperty","property_id":59},{"action":"deleteProperty","property_id":60},{"action":"deleteProperty","property_id":61},{"action":"deleteProperty","property_id":62},{"action":"deleteProperty","property_id":63},{"action":"deleteProperty","property_id":64},{"action":"deleteProperty","property_id":65},{"action":"deleteProperty","property_id":66},{"action":"deleteProperty","property_id":67},{"action":"deleteProperty","property_id":68},{"action":"deleteProperty","property_id":69},{"action":"deleteProperty","property_id":70},{"action":"deleteProperty","property_id":71}]
        # Объеденить [{"action":"setItemVariants","item_id":4995036,"variant1_id":49,"variant2_id":0},{"action":"setItemVariants","item_id":4995035,"variant1_id":51,"variant2_id":0},{"action":"setItemVariants","item_id":4995034,"variant1_id":52,"variant2_id":0},{"action":"groupItems","item_ids":[4995036,4995035,4995034],"main_item_id":4995036}]

        # [{"action":"cloneItem","item_id":4995033}]
        # AND
        # [{"action":"setItemVariants","item_id":4995033,"variant1_id":49,"variant2_id":0},{"action":"setItemVariants","item_id":5003438,"variant1_id":50,"variant2_id":0},{"action":"groupItems","item_ids":[4995033,5003438],"main_item_id":4995033}]


if __name__ == '__main__':
    req = requests.get(
            url='https://vk.com/public192858688?act=market_group_items',
            cookies={
                    "remixsid": remixsid
            }
    )
    for line in req.text.splitlines():
        if line.startswith('window.initReactApplication'):
            json_line = line[line.index('{'):line.rindex('}') + 1]
            market_data = json.loads(json_line)
            csrf_hash = market_data['options']['csrf_hash']
            break

    sizes = '104-110/56/52,110-116/60/54,116-122/64/57,86-92/52/51,92-98/56/51'.split(',')
    action_list = []

    property_response = get_request(f'[{{"action":"addProperty","title":"Размер","type":"text"}}]', hash=csrf_hash,
                                    group_id=group_id)
    prop_id = get_id(property_response)
    sizes_dict = dict()
    for size in sizes:

        action = f'[{{"action": "addVariant", "property_id": {str(int(prop_id))}, "title": "{size}"}}]'
        resp_json = get_request(action, hash=csrf_hash, group_id=group_id)
        item_id = get_id(resp_json)
        sizes_dict[size] = item_id
        if item_id == 0:
            print(f"ERROR in album too much sizes")
            break
        time.sleep(0.3)

    item_id = '5089951'
    for size in sizes:
        action_list.append({
                "action" : "cloneItem",
                "item_id": item_id
        })
    action = json.dumps(action_list[:-1])
    resp_json = get_request(action, hash=csrf_hash)
    pprint(resp_json)

    clone_ids =[item_id]+[x[0] for x in resp_json['payload'][1][0]['data']]
    action_list=[]
    for size,clone_id in zip(sizes,clone_ids):
        action_list.append({
                "action": "setItemVariants",
                "item_id": clone_id,
                "variant1_id": sizes_dict[size],
                "variant2_id": 0
        })
    action_list.append({
            "action":"groupItems",
            "item_ids":clone_ids,
            "main_item_id":item_id})
    resp_json=get_request(json.dumps(action_list), hash=csrf_hash)
    pprint(resp_json)