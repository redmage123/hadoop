#!/usr/bin/python
# this script makes assumptions about the physical environment.
#  1) each rack is its own layer 3 network with a /24 subnet, which
# could be typical where each rack has its own
#     switch with uplinks to a central core router.
#
#             +-----------+
#             |core router|
#             +-----------+
#            /             \
        #   +-----------+        +-----------+
        #   |rack switch|        |rack switch|
        #   +-----------+        +-----------+
        #   | data node |        | data node |
        #   +-----------+        +-----------+
        #   | data node |        | data node |
        #   +-----------+        +-----------+
        #
        # 2) topology script gets list of IP's as input, calculates network address, and prints '/network_address/ip'.

        import netaddr
        import sys
        sys.argv.pop(0)                                                  # discard name of topology script from argv list as we just want IP addresses

        netmask = '255.255.255.0'                                        # set netmask to what's being used in your environment.  The example uses a /24

        for ip in sys.argv:                                              # loop over list of datanode IP's
            address = '{0}/{1}'.format(ip, netmask)                      # format address string so it looks like 'ip/netmask' to make netaddr work
            try:
                   network_address = netaddr.IPNetwork(address).network     # calculate and print network address
                      print "/{0}".format(network_address)
            except:
                   print "/rack-unknown"                                    # print catch-all value if unable to calculate network address
