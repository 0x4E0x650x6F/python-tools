#!/usr/bin/env python
# encoding: utf-8

import re
import sys
import unicodedata
from multiprocessing import Pool
from string import ascii_lowercase
from urllib2 import urlopen, Request, URLError, HTTPError

pagination_re = re.compile(r"<p>(\d+) .* - (\d+) .*</p>")


def get_page(args):
    """
        Download the page
    """
    charecter, length, page_number = args
    base_url = "http://www.dicionarioinformal.com.br/caca-palavras/%s-letras/%s-----------/%s/"
    url = base_url % (length, charecter, page_number)
    print "[*]\t%s" % url
    try:
        request = Request(url=url)
        response = urlopen(request, timeout=10)
        print "[*]\tGot responce from %s" % url
        html = response.read().decode('iso-8859-1').encode('utf8')
        return html
    except HTTPError, e:
        print '[*]\tThe server couldn\'t fulfill the request.'
        print '[*]\tError code: ', e.code
    except URLError, e:
        print '[*]\tWe failed to reach a server.'
        print '[*]\tReason: ', e.reason
    except Exception, e:
        raise e


def get_words(args):
    return parse_words(get_page(args))


def main(length, initial_char):
        char_indx = ascii_lowercase.find(initial_char)
        for charecter in ascii_lowercase[char_indx:]:
            pool = Pool(processes=3)
            try:
                words = []
                fname = "pt-%s-%s" % (length, charecter)
                html = get_page((charecter, length, 1))
                fwords = parse_words(html)
                if fwords:
                    words.extend(fwords)
                number_pages_match = pagination_re.search(html)
                num_pages = number_pages_match.group(1)
                num_total_words = int(number_pages_match.group(2))
                if num_pages > 1:
                    page_mapping = [(charecter, length, index) for index in range(2, int(num_pages) + 1)]
                    results = pool.map(get_words, page_mapping)
                    print"[*]\tAppending resutls to list"
                    for fwords in results:
                        if fwords:
                            words.extend(fwords)
                print "[*]\ttotal words found %s total words expected %s" % (len(words), num_total_words)
                save_data(words, fname)
                pool.close()
                pool.join()
            except KeyboardInterrupt:
                pool.terminate()
                sys.exit(1)
                print "[*]\nYou cancelled the program!"
            finally:
                pool.close()
                pool.terminate()


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
    if len(sys.argv) != 3:
        print "[*]\targs missing script.py length initial char", len(sys.argv)
        sys.exit(1)
    length, init_char = sys.argv[1:]

    try:
        main(length, init_char)
    except KeyboardInterrupt:
        sys.exit(0)
