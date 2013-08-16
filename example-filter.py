def mfilter(filename, topic, payload):
    '''Return a tuple [pub, newpayload] indicating whether this event
       should be published (True or False) and a new payload string
       or None'''

    print "Filter for topic %s" % topic

    if filename.endswith('.jpg'):
        return False, None

    if payload is not None:
        return True, payload.replace("\n", "-").replace(" ", "+")
    return True, None
