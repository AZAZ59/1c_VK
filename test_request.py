import time
from pprint import pprint

import requests
import json



# act=load_items&al=1&group_id=192858688&hash=dc5f24945c0b68ff2b
from config import remixsid


def main():
    for k in range(15, 50):
        prop_resp=get_request('[{"action":"addProperty","title":"'+f'prop: {k}'+'","type":"text"}]')
        prop_id= get_id(prop_resp)
        for i in range(1, 150):
            action = '[{"action": "addVariant", "property_id": '+str(int(prop_id))+', "title": "' + f'item {i}' + '"}]'
            resp_json = get_request(action)
            item_id=get_id(resp_json)
            print(f'prop: {k}; item: {i}')
            if item_id ==0:
                break
            time.sleep(0.3)
        print('='*120)
        # [{"action":"addProperty","title":"New_Prop","type":"text"}]
        # [{"action":"addVariant","property_id":33,"title":"1"}]
        # Удалить много [{"action":"deleteProperty","property_id":42},{"action":"deleteProperty","property_id":43},{"action":"deleteProperty","property_id":44},{"action":"deleteProperty","property_id":45},{"action":"deleteProperty","property_id":46},{"action":"deleteProperty","property_id":47},{"action":"deleteProperty","property_id":48},{"action":"deleteProperty","property_id":49},{"action":"deleteProperty","property_id":50},{"action":"deleteProperty","property_id":51},{"action":"deleteProperty","property_id":52},{"action":"deleteProperty","property_id":53},{"action":"deleteProperty","property_id":54},{"action":"deleteProperty","property_id":55},{"action":"deleteProperty","property_id":57},{"action":"deleteProperty","property_id":58},{"action":"deleteProperty","property_id":59},{"action":"deleteProperty","property_id":60},{"action":"deleteProperty","property_id":61},{"action":"deleteProperty","property_id":62},{"action":"deleteProperty","property_id":63},{"action":"deleteProperty","property_id":64},{"action":"deleteProperty","property_id":65},{"action":"deleteProperty","property_id":66},{"action":"deleteProperty","property_id":67},{"action":"deleteProperty","property_id":68},{"action":"deleteProperty","property_id":69},{"action":"deleteProperty","property_id":70},{"action":"deleteProperty","property_id":71}]
        # Объеденить [{"action":"setItemVariants","item_id":4995036,"variant1_id":49,"variant2_id":0},{"action":"setItemVariants","item_id":4995035,"variant1_id":51,"variant2_id":0},{"action":"setItemVariants","item_id":4995034,"variant1_id":52,"variant2_id":0},{"action":"groupItems","item_ids":[4995036,4995035,4995034],"main_item_id":4995036}]

        #[{"action":"cloneItem","item_id":4995033}]
        #AND
        #[{"action":"setItemVariants","item_id":4995033,"variant1_id":49,"variant2_id":0},{"action":"setItemVariants","item_id":5003438,"variant1_id":50,"variant2_id":0},{"action":"groupItems","item_ids":[4995033,5003438],"main_item_id":4995033}]


def get_id(resp_json):
    try:
        return resp_json['payload'][1][0]['data'][0]
    except:
        print(resp_json)


def get_request(action):
    req = requests.post(
        url='https://vk.com/al_market_manage_items.php',
        data={
            "act"     : "call_action",
            "actions" : action,
            "al"      : 1,
            "group_id": 192858688,
            "hash"    : "dc5f24945c0b68ff2b",
            "lock_ver": 7600
        },
        cookies={
            "remixsid":remixsid
        }
    )
    resp_json = json.loads(req.text[4:])
    return resp_json


if __name__ == '__main__':
    # print(get_request(
    #     '[{"action":"getProperty","property_id":72}]'
    # ))
    print(get_request(
        '[{"action":"getProperty","property_id":72}]'
    ))
    #https://vk.com/public192858688?act=market_group_items   ===> window.initReactApplication('MarketItemsAdmin',"<JSON>")
    q = '{"properties":[{"id":30,"name":"Размер","type":"text","variants":[{"id":49,"name":"72\/140","value":""},{"id":50,"name":"76\/146","value":""},{"id":51,"name":"80\/152","value":""},{"id":52,"name":"90\/160","value":""},{"id":54,"name":"1234","value":""},{"id":55,"name":"qwe","value":""}]},{"id":60,"name":"prop: 18","type":"text","variants":[{"id":813,"name":"item 30","value":""},{"id":1145,"name":"123","value":""}]}],"variants":[{"property_id":30,"id":49,"value":"","name":"72\/140"},{"property_id":30,"id":50,"value":"","name":"76\/146"},{"property_id":30,"id":51,"value":"","name":"80\/152"},{"property_id":30,"id":52,"value":"","name":"90\/160"},{"property_id":30,"id":54,"value":"","name":"1234"},{"property_id":30,"id":55,"value":"","name":"qwe"},{"property_id":60,"id":813,"value":"","name":"item 30"},{"property_id":60,"id":1145,"value":"","name":"123"}],"albums":[{"id":31,"owner_id":0,"title":"ОСЕНЬ-ВЕСНА_(верхняя_одежда)","size":20,"last_add":1595969216,"photo_id":0,"href":"\/market-192858688?section=album_31","photo_src":false},{"id":30,"owner_id":0,"title":"МАЛЬЧИКИ","size":171,"last_add":1595700678,"photo_id":0,"href":"\/market-192858688?section=album_30","photo_src":false},{"id":29,"owner_id":0,"title":"МАЛЫШИ","size":421,"last_add":1595700336,"photo_id":0,"href":"\/market-192858688?section=album_29","photo_src":false},{"id":28,"owner_id":0,"title":"КР","size":407,"last_add":1595699523,"photo_id":0,"href":"\/market-192858688?section=album_28","photo_src":false},{"id":27,"owner_id":0,"title":"ЗИМА_(верхняя_одежда)","size":107,"last_add":1595698374,"photo_id":0,"href":"\/market-192858688?section=album_27","photo_src":false},{"id":26,"owner_id":0,"title":"ДЕВОЧКИ","size":255,"last_add":1595698169,"photo_id":0,"href":"\/market-192858688?section=album_26","photo_src":false},{"id":25,"owner_id":0,"title":"ВЯЗКА","size":339,"last_add":1595697677,"photo_id":0,"href":"\/market-192858688?section=album_25","photo_src":false},{"id":24,"owner_id":0,"title":"БЕЛЬЕ_-_crockid","size":125,"last_add":1595697028,"photo_id":0,"href":"\/market-192858688?section=album_24","photo_src":false},{"id":23,"owner_id":0,"title":"CUBBY_пижамы-халаты-белье","size":79,"last_add":1595696784,"photo_id":0,"href":"\/market-192858688?section=album_23","photo_src":false},{"id":22,"owner_id":0,"title":"БЕЛЬЕ_-_crockid","size":1,"last_add":1595695340,"photo_id":0,"href":"\/market-192858688?section=album_22","photo_src":false},{"id":21,"owner_id":0,"title":"CUBBY_пижамы-халаты-белье","size":79,"last_add":1595695328,"photo_id":0,"href":"\/market-192858688?section=album_21","photo_src":false},{"id":20,"owner_id":0,"title":"БЕЛЬЕ_-_crockid","size":1,"last_add":1595685655,"photo_id":0,"href":"\/market-192858688?section=album_20","photo_src":false},{"id":19,"owner_id":0,"title":"CUBBY_пижамы-халаты-белье","size":79,"last_add":1595685649,"photo_id":0,"href":"\/market-192858688?section=album_19","photo_src":false},{"id":18,"owner_id":0,"title":"БЕЛЬЕ_-_crockid","size":1,"last_add":1595684252,"photo_id":0,"href":"\/market-192858688?section=album_18","photo_src":false},{"id":17,"owner_id":0,"title":"CUBBY_пижамы-халаты-белье","size":79,"last_add":1595684247,"photo_id":0,"href":"\/market-192858688?section=album_17","photo_src":false},{"id":16,"owner_id":0,"title":"БЕЛЬЕ_-_crockid","size":1,"last_add":1595683181,"photo_id":0,"href":"\/market-192858688?section=album_16","photo_src":false},{"id":15,"owner_id":0,"title":"CUBBY_пижамы-халаты-белье","size":79,"last_add":1595683176,"photo_id":0,"href":"\/market-192858688?section=album_15","photo_src":false},{"id":2,"owner_id":0,"title":"ПИЖАМЫ_-_ХАЛАТЫ","size":3,"last_add":1595677454,"photo_id":0,"href":"\/market-192858688?section=album_2","photo_src":false}],"options":{"group_id":192858688,"csrf_hash":"dc5f24945c0b68ff2b","csrf_hash_reorder":"7d0928b09e984cbe5f","items_count":2247,"lock_ver":1256,"propertyLimits":{"MAX_PROPERTIES_PER_OWNER":30,"MAX_PROPERTY_NAME_LENGTH":50,"MAX_VARIANTS_PER_PROPERTY":30,"MAX_VARIANT_NAME_LENGTH":60,"MAX_VARIANT_VALUE_LENGTH":10}}}'
    pprint(json.loads(q))
    # main()




