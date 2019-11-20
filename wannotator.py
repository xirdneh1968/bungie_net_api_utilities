#!/usr/bin/env python3

# Script to add text annontation to 48klocs' fantastic DestinyItemManager (DIM) 
# wishlist files/feature. For the details of DIM wishlist file format:
#   https://github.com/DestinyItemManager/DIM/blob/master/docs/COMMUNITY_CURATIONS.md
# For details on DIM:
#   https://www.destinyitemmanager.com/
# Consider supporting the DIM develoment effort:
#   https://opencollective.com/dim?utm_campaign=dim&utm_medium=github&utm_source=opencollective#about_us

from collections import defaultdict, Counter
from functools import lru_cache
import argparse
import re
import json
import bungie_net_api
import sys

def handleArgs():

    parser = argparse.ArgumentParser(description='annotates wishlist with the text from hashes as comments.')
    parser.add_argument('--file', help='wishlist to process', required=True)
    _args = parser.parse_args()

    return _args

@lru_cache(maxsize=None)
def hash_to_name(hash_val):

    special = False
    trash = False

#    print('DEBUG hash_to_name:', hash_val)

    if (int(hash_val) < 0):
        if (int(hash_val) == -69420):
            special = True
        trash = True
        hash_val = str(abs(int(hash_val)))
       
    if (not special):   
        item_call = bungie_net_api.get_item_by_hash(entity_type = 'DestinyInventoryItemDefinition'
                      , hash_identifier = hash_val)
#        print(json.dumps(item_call['Response'], indent=4, sort_keys=True))
        try:
            if (trash):
                item_name = '[trash]' + item_call['Response']['displayProperties']['name'] + '[trash]'
            else:
                item_name = item_call['Response']['displayProperties']['name']
        except KeyError: 
            item_name = "hash_value" + "(" + hash_val + ")" + " not found"

    else:
        item_name = '*wildcard*'

    return item_name

def main():

    uniq_item = {}

    args = handleArgs()

    wishlist = args.file
    uniq_item = Counter()

    for line in open(wishlist):

        line = line.strip()
        match = re.match("^dimwishlist:", line)
        if match:
            (item, other) = line.split('dimwishlist:',1)[1].split('&',2)
            hash_val = item.split('item=',2)[1]
#            print('DEBUG: hash_val({0:s})'.format(hash_val))
            item_name = hash_to_name(hash_val)
            item_name.strip()
            perk_names = []
            perk_str = ''
            perk_val_str = ''
#            name_str = ''
#            name_str = name_str + item_name
            if (re.match(".*#notes:.*", other)):
                (perks, notes) = other.split('#notes:', 2)
                perks = list(perks.split('perks=', 2)[1].split(','))
                for p in perks:
                    pn = hash_to_name(p)
                    perk_names.append(pn)
                    perk_val_str = perk_val_str + '_' + p
                for n in perk_names:
                    perk_str = perk_str + ',' + n
                perk_str = '&perks=' + perk_str.lstrip(',')

#                item_hash_perks=hash_val + '-' + perk_val_str
#                uniq_item[item_hash_perks] += 1;
                item_hash_perks=item_name + perk_str
                uniq_item[item_hash_perks] += 1;

                if (uniq_item[item_hash_perks] > 1):
                    print('// [duplicate] dimwishlist:item={0:s}{1:s}#notes:{2:s}'.format(item_name, perk_str, notes))
                    print('// [duplicate] dimwishlist:item={0:s}&{1:s}{2:s}'.format(hash_val, other, notes))
                else:
                    print('// dimwishlist:item={0:s}{1:s}#notes:{2:s}'.format(item_name, perk_str, notes))
                    print('dimwishlist:item={0:s}&{1:s}{2:s}'.format(hash_val, other, notes))
            else:
                perks = list(other.split('perks=', 2)[1].split(','))
                for p in perks:
                    pn = hash_to_name(p)
                    perk_names.append(pn)
                    perk_val_str = perk_val_str + '_' + p
                for n in perk_names:
                    perk_str = perk_str + ',' + n
                perk_str = '&perks=' + perk_str.lstrip(',')    

#                item_hash_perks=hash_val + '-' + perk_val_str
#                uniq_item[item_hash_perks] += 1;
                item_hash_perks=item_name + perk_str
                uniq_item[item_hash_perks] += 1;
               
                if (uniq_item[item_hash_perks] > 1):
                    print('// [duplicate] dimwishlist:item={0:s}{1:s}'.format(item_name, perk_str))
                    print('// [duplicate] dimwishlist:item={0:s}&{1:s}'.format(hash_val,other))
                else:
                    print('// dimwishlist:item={0:s}{1:s}'.format(item_name, perk_str))
                    print('dimwishlist:item={0:s}&{1:s}'.format(hash_val,other))
        else:
            print(line)
       
    print(hash_to_name.cache_info(), file=sys.stderr)

    print(uniq_item.items())

if __name__ == '__main__':
    main()
