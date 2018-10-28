import re
import time
from pprint import pformat

import tweepy

from SocialNetworkHarvester.harvest.utils import check_stop_flag_raised
from Twitter.harvest.globals import clients_queue


class Client:
    # refreshTimer = MAX_INT
    calls_map = {
        # 'callName' : 'callIdentifier',
        'lookup_users': '/users/lookup',
        'friends_ids': '/friends/ids',
        'rate_limit_status': '/application/rate_limit_status',
        'followers_ids': '/followers/ids',
        'favorites': '/favorites/list',
        'user_timeline': '/statuses/user_timeline',
        'retweets': '/statuses/retweets/:id',
        'statuses_lookup': '/statuses/lookup',
    }
    name = "Unnamed client"
    limits = None

    def __str__(self):
        return self.name

    def __init__(self, **kwargs):
        ck = kwargs['ck']
        cs = kwargs['cs']
        atk = kwargs['atk']
        ats = kwargs['ats']
        if "name" in kwargs:
            self.name = kwargs['name']
        auth = tweepy.OAuthHandler(ck, cs)
        auth.set_access_token(atk, ats)
        self.api = tweepy.API(auth)
        self.refresh_limits()

    def call(self, call_name, *args, **kwargs):
        if time.time() >= self.get_teset_time(call_name) + 1:
            self.refresh_limits()
        remaining_calls = self.get_remaining_calls(call_name)
        if remaining_calls > 0:
            self.set_remaining_calls(call_name, remaining_calls - 1)
            return getattr(self.api, call_name)(*args, **kwargs)
        else:
            raise Exception('No more calls of type "%s"' % self.calls_map[call_name])

    def refresh_limits(self):
        response = self.api.rate_limit_status()
        self.limits = response['resources']
        # self.prettyLimitStatus()

    def get_remaining_calls(self, call_name):
        if time.time() >= self.get_teset_time(call_name) + 1:
            self.refresh_limits()
        call_identifier = self.calls_map[call_name]
        return self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]['remaining']

    def set_remaining_calls(self, call_name, value):
        call_identifier = self.calls_map[call_name]
        self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]['remaining'] = value

    def get_teset_time(self, call_name):
        call_identifier = self.calls_map[call_name]
        # log('item found: %s'%re.search(r'(?<=/)\w+(?=/)', callIdentifier))
        return self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]['reset']

    def pretty_limit_status(self):
        ret = {'client': str(self)}
        for call_name in self.calls_map:
            call_identifier = self.calls_map[call_name]
            ret["{:<20}".format(call_name)] = "{}/{} (resets in {:0.0f} seconds)".format(
                self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]['remaining'],
                self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]['limit'],
                self.limits[re.search(r'(?<=/)\w+(?=/)', call_identifier).group(0)][call_identifier]
                ['reset'] - time.time())
        return pformat(ret)


def get_client(call_name):
    client = None
    if not clients_queue.empty():
        client = clients_queue.get()
    while not client or client.get_remaining_calls(call_name) <= 0:
        check_stop_flag_raised()
        if client:
            clients_queue.put(client)
            client = None
        if not clients_queue.empty():
            client = clients_queue.get()
    # client.pretty_limit_status()
    return client


def return_client(client):
    if clients_queue.full():
        # log("clients: %s"%[client for client in iter(clients_queue.get, None)])
        raise Exception("Client Queue is already full. There is a Client that is returned twice!")
    else:
        clients_queue.put(client)
        # log("returned client. %i clients available"%clients_queue.qsize())


class CustomCursor:
    results = []
    index = 0
    nbItems = 0
    pagination_type = None
    pagination_item = None

    def __init__(self, call_name, **kwargs):
        self.call_name = call_name
        self.kwargs = kwargs
        self.init_pagination()

    def init_pagination(self):
        client = get_client(self.call_name)
        method = getattr(client.api, self.call_name)
        if not hasattr(method, 'pagination_mode'):
            raise Exception("The API method must support pagination to be used with a Cursor.")
        elif method.pagination_mode == 'cursor':
            # log('cursor-type pagination')
            self.pagination_type = 'cursor'
            self.pagination_item = -1
        elif method.pagination_mode == 'page':
            # log('page-type pagination')
            self.pagination_type = 'page'
            self.pagination_item = 0
        elif method.pagination_mode == 'id':
            # log('id-type pagination')
            self.pagination_type = 'max_id'
            self.pagination_item = None
        return_client(client)

    def next(self):
        check_stop_flag_raised()
        if self.index == -1:
            return None
        if self.index < self.nbItems:
            item = self.results[self.index]
            self.index += 1
            return item
        else:
            self._get_next_set()
            return self.next()

    def _get_next_set(self):
        self.results = []

        self.kwargs[self.pagination_type] = self.pagination_item
        client = get_client(self.call_name)
        try:
            if self.pagination_type == 'cursor':
                self.results, cursors = client.call(self.call_name, **self.kwargs)
                self.pagination_item = cursors[1]
            elif self.pagination_type == 'max_id':
                self.results = client.call(self.call_name, **self.kwargs)
                self.pagination_item = self.results.max_id
            elif self.pagination_type == 'page':
                self.results = client.call(self.call_name, **self.kwargs)
                self.pagination_item += 1
            # log('%s: %s'%(self.pagination_type,self.pagination_item))
        except Exception:
            # twitterLogger.exception('an error occured in cursor')
            return_client(client)
            raise
        return_client(client)
        self.nbItems = len(self.results)
        if self.nbItems == 0:
            self.index = -1  # means the iteration has finished
        else:
            self.index = 0
