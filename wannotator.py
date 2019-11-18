#!/usr/bin/env python3

# Script to add text annontation to 48klocs' fantastic DestinyItemManager (DIM) 
# wishlist files/feature. For the details of DIM wishlist file format:
#   https://github.com/DestinyItemManager/DIM/blob/master/docs/COMMUNITY_CURATIONS.md
# For details on DIM:
#   https://www.destinyitemmanager.com/
# Consider supporting the DIM development effort:
#   https://opencollective.com/dim?utm_campaign=dim&utm_medium=github&utm_source=opencollective#about_us

from functools import lru_cache
import argparse
import re
import json
import bungie_net_api

def handleArgs():

    parser = argparse.ArgumentParser(description='annotates wishlist with the text from hashes as commnents.')
    parser.add_argument('--file', help='wishlist to process', required=True)
    _args = parser.parse_args()

    return _args

@lru_cache(maxsize=None)
def hash_to_name(hash_val):
    item_call = bungie_net_api.get_item_by_hash(entity_type = 'DestinyInventoryItemDefinition'
                  , hash_identifier = hash_val)
#    print(json.dumps(item_call['Response'], indent=4, sort_keys=True))
    try:
        item_name = item_call['Response']['displayProperties']['name']
    except KeyError: 
        item_name = "hash_value" + "(" + hash_val + ")" + " not found"

    return item_name

def main():

    args = handleArgs()

    wishlist = args.file

    for line in open(wishlist):

        line = line.strip()
        match = re.match("^dimwishlist:", line)
        if match:
            (item, other) = line.split('dimwishlist:',1)[1].split('&',2)
            hash_val = item.split('item=',2)[1]
            item_name = hash_to_name(hash_val)
            item_name.strip()
            perk_names = []
            perk_str = ''
#            name_str = ''
#            name_str = name_str + item_name
            if (re.match(".*#notes:.*", other)):
                (perks, notes) = other.split('#notes:', 2)
                perks = list(perks.split('perks=', 2)[1].split(','))
                for p in perks:
                    pn = hash_to_name(p)
                    perk_names.append(pn)
                for n in perk_names:
                    perk_str = perk_str + ',' + n
                perk_str = '&perks=' + perk_str.lstrip(',')
                print('// dimwishlist:item={0:s}{1:s}#notes:{2:s}'.format(item_name, perk_str, notes))
                print('dimwishlist:item={0:s}&{1:s}{2:s}'.format(hash_val, other, notes))
            else:
                perks = list(other.split('perks=', 2)[1].split(','))
                for p in perks:
                    pn = hash_to_name(p)
                    perk_names.append(pn)
                for n in perk_names:
                    perk_str = perk_str + ',' + n
                perk_str = '&perks=' + perk_str.lstrip(',')    
                print('// dimwishlist:item={0:s}{1:s}'.format(item_name, perk_str))
                print('dimwishlist:item={0:s}&{1:s}'.format(hash_val,other))
        else:
            print(line)
       
#    print(hash_to_name.cache_info())

if __name__ == '__main__':
    main()
