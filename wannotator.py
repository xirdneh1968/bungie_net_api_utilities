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
    parser.add_argument('--duplicates', help='comment out duplicate entries', required=False)
    _args = parser.parse_args()

    return _args

@lru_cache(maxsize=None)
def hash_to_name(hash_val):

    special = False
    trash = False
    entity_param = ''

#    print('DEBUG hash_to_name:', hash_val)

    if (int(hash_val) < 0):
        if (int(hash_val) == -69420):
            special = True
        trash = True
        hash_val = str(abs(int(hash_val)))
        entity_param = 'DestinyInventoryItemDefinition'
    elif (0 <= int(hash_val) <= 58):
        entity_param = 'DestinyItemCategoryDefinition'
    else:
        entity_param = 'DestinyInventoryItemDefinition'
       
    if (not special):   
        item_call = bungie_net_api.get_item_by_hash(entity_type = entity_param
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
    if (args.duplicates):
        comment_dupes = 1
    else:
        comment_dupes = 0

    for line in open(wishlist):

        line = line.strip()
        match = re.match("^dimwishlist:", line)
        if match:
#            print("DEBUG - line:", line)
##            (item, other) = line.split('dimwishlist:',1)[1].split('&',2)
            wl = re.compile(r'^dimwishlist:(item=[0-9-]*)\s*((&perks=|#notes:).*)')
            dwl = wl.match(line)
            item = dwl.group(1)
            other = dwl.group(2)
            hash_val = item.split('item=',2)[1]
#            print('DEBUG: hash_val({0:s})'.format(hash_val))
            item_name = hash_to_name(hash_val)
            item_name.strip()
            perk_names = []
            perk_str = ''
            perk_val_str = ''
##            if (re.match(".*#notes:.*", other)):
            if (re.match("^&perks=", other)):
#                print("DEBUG - other >", end="")
#                print(other, end="")
#                print("< \n", end="")
                re_perks = re.compile(r'^&perks=([\d,]*)(#notes:)?(.*)')
                match_perks = re_perks.match(other)
#                print("DEBUG - match_perks: ", match_perks, "\n")
                perks = list(match_perks.group(1).split(','))
                notes = match_perks.group(3)
            elif (re.match("^#notes:.*", other)):
                notes = other.split('#notes:', 2)[1]
            else:
                perks = list(other.split('&perks=', 2)[1].split(','))

            for p in perks:
                pn = hash_to_name(p)
                perk_names.append(pn)
                perk_val_str = perk_val_str + '_' + p
            for n in perk_names:
                perk_str = perk_str + ',' + n
            perk_str = '&perks=' + perk_str.lstrip(',') 

#            item_perks_hash=item_name + perk_str
            # item_perks_hash needs to be built based on numerical item and perk values to accomodate multiple versions
            # of same item such as fixed roll / random roll
            item_perks_hash=hash_val + perk_val_str
            uniq_item[item_perks_hash] += 1;  

            if (re.match("^#notes:.*", other)):
#                print("DEBUG ^#notes: match other")
                if (uniq_item[item_perks_hash] > 1):
                    print('// [duplicate {2:d}] dimwishlist:item={0:s}#notes:{1:s}'.format(item_name, notes, uniq_item[item_perks_hash]))
                    if (comment_dupes):
                        print('// [duplicate {2:d}] dimwishlist:item={0:s}#notes:{1:s}'.format(hash_val, notes, uniq_item[item_perks_hash]))
                    else:
                        print('dimwishlist:item={0:s}#notes:{1:s}'.format(hash_val, notes ))
                else:
                    print('// dimwishlist:item={0:s}#notes:{1:s}'.format(item_name, notes))
                    print('dimwishlist:item={0:s}#notes:{1:s}'.format(hash_val, notes))
            else:
                if (uniq_item[item_perks_hash] > 1):
                    print('// [duplicate {2:d}] dimwishlist:item={0:s}{1:s}'.format(item_name, perk_str, uniq_item[item_perks_hash]))
                    if (comment_dupes):
                        print('// [duplicate {2:d}] dimwishlist:item={0:s}{1:s}'.format(hash_val,other, uniq_item[item_perks_hash]))
                    else:
                        print('dimwishlist:item={0:s}{1:s}'.format(hash_val, other))
                else:
                    print('// dimwishlist:item={0:s}{1:s}'.format(item_name, perk_str))
                    print('dimwishlist:item={0:s}{1:s}'.format(hash_val,other))

        else:
            print(line)
    
    print("Unique items summary:", file=sys.stderr)
    print(uniq_item.items(), file=sys.stderr)
    print("Cache performance:", file=sys.stderr)
    print(hash_to_name.cache_info(), file=sys.stderr)

if __name__ == '__main__':
    main()
