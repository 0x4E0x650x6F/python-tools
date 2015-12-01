#!/usr/bin/env python
# encoding: utf-8

import re
import sys
import unicodedata
from multiprocessing import Pool
from string import ascii_lowercase
from urllib2 import urlopen, URLError, HTTPError


def get_page(args):
    """
        Download the page
    """
    charecter, length, page_number = args
    base_url = "http://www.dicionarioinformal.com.br/caca-palavras/%s-letras/%s-----------/%s/"
    url = base_url % (length, charecter, page_number)
    print "[*]\t%s" % url
    try:
        response = urlopen(url)
        html = response.read().decode('iso-8859-1').encode('utf8')
        return html
    except HTTPError, e:
        print '[*]\tThe server couldn\'t fulfill the request.'
        print '[*]\tError code: ', e.code
    except URLError, e:
        print '[*]\tWe failed to reach a server.'
        print '[*]\tReason: ', e.reason


def main(length):
    pool = Pool(processes=3)
    try:
        for charecter in ascii_lowercase:
            words = []
            fname = "pt-%s-%s" % (length, charecter)
            pagination_re = re.compile(r"<p>(\d+) .* - (\d+) .*</p>")
            html = get_page((charecter, length, 1))
            fwords = parse_words(html)
            if fwords:
                words.extend(fwords)
            number_pages_match = pagination_re.search(html)
            num_pages = number_pages_match.group(1)
            num_total_words = int(number_pages_match.group(2))
            if num_pages > 1:
                page_mapping = [(charecter, length, index) for index in range(2, int(num_pages) + 1)]
                results = pool.map(get_page, page_mapping)
                for html in results:
                    fwords = parse_words(html)
                    if fwords:
                        words.extend(fwords)
            print "[*]\ttotal words found %s total words expected %s" % (len(words), num_total_words)
            save_data(words, fname)
    except KeyboardInterrupt:
        pool.terminate()
        print "[*]\nYou cancelled the program!"
        sys.exit(1)


def save_data(word_lst, filename):
    print "[*]\tSaveing words"
    with open(filename + "-utf8.dic", 'w') as udictionary, open(filename +
                                                                "-ascii.dic", 'w') as dict:
        udictionary.write("\n".join(word_lst).lower())
        dict.write(unicodedata.normalize(
            'NFKD', unicode("\n".join(word_lst).lower(), 'utf8')).encode('ascii', 'ignore'))


def parse_words(html):
    words_re = re.compile(r"<li><a.*alt=\"Significado de.*\".*>(.*)</a></li>")
    return words_re.findall(html)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "[*]\targs missing script.py length"
        sys.exit(1)
    length = sys.argv[1]
    main(length)
