# -*- coding: utf-8 -*-
#
# Copyright (c) 2012, Xabier (slok) Larrakoetxea <slok69 [at] gmail [dot] com>
#
# 3 clause/New BSD license:
# opensource: http://www.opensource.org/licenses/BSD-3-Clause
# wikipedia: http://en.wikipedia.org/wiki/BSD_licenses
#


import sys
if sys.hexversion < 0x020700f0:   # hex number for 2.7.0 final release
    sys.exit("Python 2.7.0 or newer is required to run this program.")
import re
import timeit
import argparse
from multiprocessing import Pool
if sys.version_info[0] < 3:
    import urllib2
else:
    import urllib.request as urllib2


def partition_data(items):
    """Cuts data in parts. This parts is the data that will receive each of
    the workers
    :param items: Iterable containing all the data to process
    """
    # Get the number of data for each process (int for python 3)
    number_to_split = int(len(items) / WORKERS)

    # Create a list with lists
    for i in range(WORKERS + 1):
        yield(items[i * number_to_split:(i + 1) * (number_to_split)])

    # Add the remaining data
    remaining_group = items[(i + 1) * number_to_split:]
    if remaining_group:
        yield(remaining_group)


def map_function(words):
    """This function will apply some logic to the data that will receive
    :param words: List of words
    """
    # Apply the logic to the raw data
    result = {}
    for i in words:
        try:
            result[i] += 1
        except KeyError:
            result[i] = 1
    return result


def reduce_function(sub_mapping):
    """This function will reduce all the results that all the maps have process
    :param sum_mapping: All the results of the maps executed
    """
    # Reduce all the data by combining all the parts that are received
    result = {}
    for i in sub_mapping:
        for k, v in i.items():
            try:
                result[k] += v
            except KeyError:
                result[k] = v
    return result


def mapreduce(all_items):
    """The start point for the mapreduce process
    :param all_items: Iterable with all the data to process
    """
    #Group the items for each worker
    group_items = list(partition_data(all_items))

    #Call the map functions concurently with a pool of processes
    pool = Pool(processes=WORKERS)
    sub_map_result = pool.map(map_function, group_items)

    #Reduce all the data captured
    return reduce_function(sub_map_result)


def get_data(url, times):
    """Get the data from the urls to process wit mapreduce or classic style
    :param url: The url to download the data
    :param times: The times to multiply the downloaded data (moar data!!!)
    """
    #Get words and create a list with all the chars
    data = urllib2.urlopen(url).read()
    data = str(data) if sys.version_info[0] >= 3 else data
    data = re.sub(r'[\.\,\\n\;\:]', '', data)

    return list(data * times)


def not_mapreduce(all_items):
    """Use the map function for all the data so we are using classic style
    :param all_items: Iterable with all the data to process
    """
    return map_function(all_items)


def show_items(items):
    """Prints the items in a 'beautiful' way
    :param items: The items to print in a proper style
    """
    #Sort the items before printing
    sorted_items = sorted(items.items(), key=lambda x: x[1], reverse=True)
    for i in sorted_items:
        print("'%s' - %i" % i)

if __name__ == '__main__':
    #Set arguments
    parser = argparse.ArgumentParser(description="Mapreduce simple example")

    #Add non exclusive args (benchmark, times, url)
    parser.add_argument('-u', '--url',
                        help="URL to get the text",
                        type=str,
                        required=False,
                        default='http://bit.ly/raw-lorem-ipsum')
    parser.add_argument('-t', '--times',
                        type=int,
                        default=1,
                        help="times to duplicate the processing data",
                        required=False)
    parser.add_argument('-b', '--benchmark',
                        action="store_true",
                        help="benchmark time",
                        required=False)

    #Add special arg for benchmarks (we need to check manually)
    parser.add_argument('-r', '--repeat',
                        type=int,
                        help="number of iterations the test will repeat",
                        required=False)

    #Add exclusive args (not mapreduce and workers) workers ar exclusive of
    #mapreduce method
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-w', '--workers',
                        help="Number of workers for the map reduce",
                        type=int,
                        required=False,
                        default=15)
    group.add_argument('-n', '--notmapreduce',
                        action="store_true",
                        help="Without mapreduce method",
                        required=False)

    args = parser.parse_args()

    test_times = args.repeat
    # Manual Check if -r is with -b
    if not args.benchmark and args.repeat:
        parser.error('argument -r/--repeat: must be used with -b/--benchmark')
    elif args.benchmark and not args.repeat:
        test_times = 1

    #Start program
    final_result = {}
    WORKERS = args.workers
    all_items = get_data(args.url, args.times)

    #Check what tipe of execution is:
    # -mapreduce regular
    # -not mapreduce regular
    # -mapreduce benchmark
    # -notmapreduce benchmark
    if args.notmapreduce and args.benchmark:
        t = timeit.Timer('not_mapreduce(all_items)',
                        'from __main__ import not_mapreduce, all_items')
        print('Not mapreduce: %f' % t.timeit(number=test_times))

    elif not args.notmapreduce and args.benchmark:
        t = timeit.Timer('mapreduce(all_items)',
                        'from __main__ import mapreduce, all_items')
        print('Mapreduce: %f' % t.timeit(number=test_times))

    elif args.notmapreduce:
        print("Not Mapreduce")
        print("-" * 50)
        show_items(not_mapreduce(all_items))
    else:
        print("Mapreduce")
        print("-" * 50)
        show_items(mapreduce(all_items))
