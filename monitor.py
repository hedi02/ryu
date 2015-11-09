from operator import attrgetter

#from ryu.app import simple_switch_13
import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from varfile import *
import time

start_time = time.time()

class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    cookielist = [] #list to keep flow/cookie stat
    pktlist = []
    bytelist = []
    byteprevious=[0] #byte increment for every flow stat reply

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if not datapath.id in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(monperiod)
            print "cookie_id " + str(self.cookielist)
            print "byte " + str(self.bytelist)
            print "packet_num " + str(self.pktlist)
            print("--- %s seconds ---" % (time.time() - start_time))
            if self.bytelist:
                # print self.byteprevious
                print str(abs(self.byteprevious[0]-self.bytelist[0]))+" increment"
                print str(self.byteprevious[0]/monperiod/1000000)+" Mbps"
            print "====================="

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        body = ev.msg.body

            # self.logger.info('datapath         '
            #                  'in-port  eth-dst           '
            #                  'out-port packets  bytes')
        for stat in sorted([flow for flow in body if flow.priority == 1],
                           key=lambda flow: (flow.match['in_port'],
                                             flow.match['eth_dst'])):
            # self.logger.info('%016x %8x %17s %8x %8d %8d %8d',
            #                  ev.msg.datapath.id,
            #                  stat.match['in_port'], stat.match['eth_dst'],
            #                  stat.instructions[0].actions[0].port,
            #                  stat.packet_count, stat.byte_count, stat.cookie)

            #add statistic
            if stat.cookie in self.cookielist:
                self.byteprevious[self.cookielist.index(stat.cookie)]=self.bytelist[self.cookielist.index(stat.cookie)]
                self.cookielist[self.cookielist.index(stat.cookie)] = stat.cookie
                self.pktlist[self.cookielist.index(stat.cookie)] = stat.packet_count
                self.bytelist[self.cookielist.index(stat.cookie)] = stat.byte_count
            else:
                self.cookielist.append(stat.cookie)
                self.pktlist.append(stat.packet_count)
                self.bytelist.append(stat.byte_count)
                self.byteprevious.append(stat.byte_count)

