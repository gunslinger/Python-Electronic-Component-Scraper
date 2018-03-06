# -*- coding: utf-8 -*-

import re

def cleansplit(r_input):
    """ Clean Split.

    Clean unwanted list/string on result and return cleaned list/string

    Args:
        param1: r_input

    Returns:
        res_list
    """
    if isinstance(r_input, list):
        return [string.extract().strip(' \t\n\r') for string in r_input if string.extract().split()]
    elif r_input == None:
        return ['']
    else:
        return r_input.strip(' \t\n\r')

def listbalancer(r_input):
    """ List Balancer.

    This function will keep list balanced. and could return result scraped item list even one condition
    on spesific item is empty. this is will help parsing for example on arrow.com

    Args:
        param1: r_input

    Returns:
        res_list
    """
    res_list = []
    for a in range(len(r_input)): res_list.append('')
    return res_list

def cleanqty(string_input):
    """ Clean Quantity.

    Remove any unwanted symbol in strings such as , or . and return cleaned string for integer of quantity.

    Args:
        param1: r_input

    Returns:
        res_list
    """
    clean_qty = re.sub('[,.]', '', string_input)
    return clean_qty