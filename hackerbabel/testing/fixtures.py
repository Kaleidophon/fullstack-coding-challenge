# -*- coding: utf-8 -*-

"""
Some pre-prepared data for testing purposes.
"""

# STD
from copy import deepcopy

# PROJECT
from hackerbabel.clients.hackernews_client import (
    HackerNewsClient, DROPS, NEW_NAMES
)

STORIES = [
    {u'kids': [13421441, 13421387, 13421393, 13421406, 13421742,
               13421341, 13421644, 13421541, 13421358, 13421866,
               13421743, 13421486, 13421455, 13421368, 13421506,
               13421405, 13421945, 13421430, 13421891, 13421566,
               13421458, 13421693, 13421431, 13421361, 13421386,
               13421510, 13421396, 13421402],
     u'title': u'Obama Commutes Bulk of Chelsea Manning\u2019s Sentence',
     u'url': u'https://www.nytimes.com/2017/01/17/us/politics/obama-commutes-bulk-of-chelsea-mannings-sentence.html?_r=0',
     u'descendants': 202, u'id': 13421298, u'score': 615,
     u'time': 1484687885, u'type': u'story', u'by': u'coloneltcb'}, {
        u'kids': [13419914, 13420380, 13420170, 13420490, 13419853,
                  13420041, 13419812, 13420176, 13419833, 13421801,
                  13420018, 13421258, 13420350, 13420239, 13421209,
                  13419960, 13419974, 13421070, 13420027, 13420760,
                  13419965, 13420331, 13419991, 13420278, 13420247,
                  13419926, 13421259, 13419889, 13420059, 13420534,
                  13419948, 13419967, 13419658],
        u'title': u'How much does employee turnover really cost?',
        u'url': u'https://medium.com/latticehq/how-much-does-employee-turnover-really-cost-d61df5eed151#.p105nzhlz',
        u'descendants': 178, u'id': 13419444, u'score': 286,
        u'time': 1484675009, u'type': u'story',
        u'by': u'craigkerstiens'}, {
        u'kids': [13420044, 13421046, 13421769, 13421398, 13421186,
                  13420297, 13420323, 13420539, 13420163, 13420081,
                  13421122, 13420024, 13420019],
        u'title': u'Mo.js: motion graphics toolbelt for the web',
        u'url': u'https://github.com/legomushroom/mojs',
        u'descendants': 36, u'id': 13419665, u'score': 180,
        u'time': 1484676471, u'type': u'story', u'by': u'hunvreus'}, {
        u'kids': [13421206, 13420856, 13421894, 13421329, 13421462,
                  13421222, 13420738, 13421065, 13421183, 13420467,
                  13421200, 13420807, 13421080],
        u'title': u'Pixie \u2013 A small, fast, native Lisp',
        u'url': u'http://pixielang.org/', u'descendants': 58,
        u'id': 13420092, u'score': 101, u'time': 1484679633,
        u'type': u'story', u'by': u'throwaway7645'},
    {u'kids': [13421287, 13421823, 13421711],
     u'title': u'Large stationary gravity wave in the atmosphere of Venus',
     u'url': u'http://www.nature.com/ngeo/journal/vaop/ncurrent/full/ngeo2873.html',
     u'descendants': 5, u'id': 13421136, u'score': 24,
     u'time': 1484686786, u'type': u'story', u'by': u'bcaulfield'},
    {u'kids': [13421338, 13420518, 13420690, 13421130],
     u'title': u'The fivethirtyeight R package',
     u'url': u'http://blog.revolutionanalytics.com/2017/01/the-fivethirtyeight-r-package.html',
     u'descendants': 32, u'id': 13420231, u'score': 74,
     u'time': 1484680524, u'type': u'story', u'by': u'michaelsbradley'},
    {u'kids': [13420449, 13420246, 13421277, 13420303, 13421161,
               13420642, 13421367, 13420581, 13420836, 13421274,
               13420484, 13420554],
     u'title': u'Moving beyond localStorage',
     u'url': u'https://journal.standardnotes.org/moving-beyond-localstorage-991e3695be15#.5ua9rs4vk',
     u'descendants': 30, u'id': 13419823, u'score': 76,
     u'time': 1484677723, u'type': u'story', u'by': u'mobitar'},
    {u'kids': [13421719],
     u'title': u'LocalForage: Improved Offline Storage (IndexedDB, WebSQL or LocalStorage)',
     u'url': u'https://github.com/localForage/localForage',
     u'descendants': 2, u'id': 13421321, u'score': 14,
     u'time': 1484688050, u'type': u'story', u'by': u'vmorgulis'}, {
        u'kids': [13421524, 13421868, 13421332, 13421370, 13421365,
                  13421581],
        u'title': u'In Colorado, self-harm is leading cause of death in new mothers',
        u'url': u'http://www.cuanschutztoday.org/colorado-self-harm-leading-cause-death-new-mothers/',
        u'descendants': 10, u'id': 13420941, u'score': 21,
        u'time': 1484685366, u'type': u'story', u'by': u'baalcat'}, {
        u'kids': [13419763, 13418175, 13417807, 13419622, 13417617,
                  13417849, 13419078, 13417580, 13419999, 13417628,
                  13419975, 13418204, 13420727, 13417608, 13417566,
                  13418839],
        u'title': u'Did Pixar accidentally delete Toy Story 2 during production? (2012)',
        u'url': u'https://www.quora.com/Pixar-company/Did-Pixar-accidentally-delete-Toy-Story-2-during-production/answer/Oren-Jacob',
        u'descendants': 167, u'id': 13417037, u'score': 347,
        u'time': 1484657754, u'type': u'story', u'by': u'chenster'}
]


def get_processed_stories():
    hn_client = HackerNewsClient()
    return [
        hn_client._jsonify_story(
            story, hn_client.formatting_functions, NEW_NAMES, DROPS
        )
        for story in deepcopy(STORIES)
    ]
