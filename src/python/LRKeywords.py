#! /usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import copy
import sys

class LRKeyword():
    def __init__(self, name = '', synonyms = [], depth = 0):
        self.children = []
        self.synonyms = synonyms
        self.name = name
        self.depth = depth

    def add_child(self, child):
        self.children.append(child)
        return self.children[-1]

    def add_synonym(self, synonym = ''):
        self.synonyms.append(synonym)
        return len(self.synonyms)

    def print_keyword(self, output, depth):
        padding = '\t' * depth
        output.write(padding + self.name + '\n')
        for synonym in sorted(self.synonyms):
            padding = '\t' * (depth+1)
            output.write(padding + '{' + synonym + '}\n')

        for child in sorted(self.children):
            child.print_keyword(output, depth + 1)

    def traverse_keywords(self, func):
        """
        Traverse the keyword tree and call function func on each one
        """

        func(self)

        for child in sorted(self.children):
            child.traverse_keywords(func)


class LRKeywords():
    def __init__(self, handle = None):
        self.keywords = []
        if handle:
            self.read_keywords(handle)

    def read_keywords(self, input):
        """
        Translate keyword file into a nested structure with children (recursive)
        and synonyms.
        """

        last_level = 0
        for raw_line in input:
            line = raw_line.rstrip()
            keyword = line.lstrip()
            level = len(line)-len(keyword)
            if (len(keyword) == 0):
                continue
            if level == 0:
                keyword_stack = []
                newKeyword = LRKeyword(name=keyword, depth=level)
                self.keywords.append(copy.deepcopy(newKeyword))
                keyword_stack.append(self.keywords[-1])
                last_level = level
            elif level > last_level:
                if keyword.startswith('{'):
                    synonym = keyword.strip('{}')
                    keyword_stack[-1].add_synonym(synonym)
                else:
                    newKeyword = LRKeyword(name=keyword, depth=level)
                    kw = keyword_stack[-1].add_child(copy.deepcopy(newKeyword))
                    keyword_stack.append(kw)
                    last_level = level
            elif level <= last_level:
                for i in range(0, last_level-level+1):
                    keyword_stack.pop()
                newKeyword = LRKeyword(name=keyword, depth=level)
                kw = keyword_stack[-1].add_child(copy.deepcopy(newKeyword))
                keyword_stack.append(kw)
                last_level = level

        return

    def write_keywords(self, output):
        """
        Write a nested structure with children (recursive)
        and synonyms back out into the Adobe Lightroom formatted file.
        """
        # Fixme: add back in sorting by keyword.name with sorting function

        for keyword in self.keywords:
            keyword.print_keyword(output, 0)

    def traverse_keywords(self, keywords, func):
        for keyword in keywords:
            func(keywords[keyword])
            traverse_keywords(keywords[keyword]['children'])

        return

if __name__ == "__main__":

    """
    Convert keywords to/from Lightroom Keyword Project format from/to my format
    """

    input_file = "Lightroom Keywords - Minimal2.txt"

    input = open(input_file, 'r')

    lrk = LRKeywords(handle=input)

    print "\n\nContents\n"

    lrk.write_keywords(sys.stdout)
