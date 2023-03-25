#!/usr/bin/python3
#
# Wesleyan University
# COMP 332, Spring 2023
# Web server helper functions

# Project modules
import http_constants as const

def parse_url(url):

    url_components = url.split('http://')
    if len(url_components) > 1:
        url = '/'.join(url_components[1:])

    url_components = url.split('/')
    hostname = url_components[0]
    if len(url_components) == 1:
        pathname = '/'
    else:
        pathname = '/' + '/'.join(url_components[1:])

    return [hostname, pathname]

def create_http_req(hostname, pathname):

    # Create header lines
    get = 'GET ' + pathname + ' HTTP/1.1' + const.END_LINE
    host = 'Host: ' + hostname + const.END_LINE
    conn_type = 'Connection: close' + const.END_LINE
    char_set = 'Accept-charset: utf-8' + const.END_LINE

    # Create HTTP request
    http_req = (get + host + char_set + conn_type + const.END_LINE)

    return http_req

def add_http_field(msg, name, value):

    try:
        header_end = msg.index(const.END_HEADER) + len(const.END_LINE)
        old_header = msg[ :  header_end]
        field = name + ':' + value + const.END_LINE
        new_msg = old_header + field + const.END_LINE
        return new_msg

    except ValueError as e:
        print("Unable to add HTTP field:", e)
        return '-1'

def get_http_field(msg, name, end_str):

    try:
        name_start = msg.index(name)
        name_end = name_start + len(name)
        field_end = name_end + msg[name_end : ].index(end_str)
        value = msg[name_end : field_end]
        return value

    except ValueError as e:
        print("HTTP field not found: ", e)
        return -1

