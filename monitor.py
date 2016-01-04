from operator import attrgetter

#from ryu.app import simple_switch_13
import simple_switch_13
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
from varfile import *
import db
import time
import rest_qos
import rest_conf_switch
import thread
import subprocess


start_time = time.time()

class SimpleMonitor(simple_switch_13.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        #self.monitor_thread = hub.spawn(self._monitor2)

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


    def send_flow_mod(self, datapath):
        ofp = datapath.ofproto
        ofp_parser = datapath.ofproto_parser

        cookie = cookie_mask = 0
        table_id = 0
        idle_timeout = hard_timeout = 0
        priority = 32768
        buffer_id = ofp.OFP_NO_BUFFER
        match = ofp_parser.OFPMatch(in_port=1, eth_dst='aa:ff:ff:ff:ff:ff')
        # actions = [ofp_parser.OFPActionOutput(ofp.OFPP_NORMAL, 0)]
        actions = [ofp_parser.OFPActionSetQueue(1), ofp_parser.OFPActionOutput(2)]

        inst = [ofp_parser.OFPInstructionActions(ofp.OFPIT_APPLY_ACTIONS,
                                                 actions)]
        req = ofp_parser.OFPFlowMod(datapath, cookie, cookie_mask,
                                    table_id, ofp.OFPFC_ADD,
                                    idle_timeout, hard_timeout,
                                    priority, buffer_id,
                                    ofp.OFPP_ANY, ofp.OFPG_ANY,
                                    ofp.OFPFF_SEND_FLOW_REM,
                                    match, inst)
        datapath.send_msg(req)


    def _monitor2(self):
        while True:
            print("second_thread")
            db.printdb()
            db.bytecheck()
            hub.sleep(2)

    def _monitor(self):
        """
        executing request_stats every monperiod, stated in varfile.py.
        using for to iterate every switches
        """
        while True:
            for dp in self.datapaths.values():
                # print dp
                self._request_stats(dp)
                self.send_flow_mod(dp)
            hub.sleep(monperiod)
            #print "====================="
            #print("--- %s seconds ---" % (time.time() - start_time))

    def _request_stats(self, datapath):
        """
        sending stat request to switch
        :param datapath:
        """
        self.logger.debug('send stats request: %016x', datapath.id)
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

        req = parser.OFPPortStatsRequest(datapath, 0, ofproto.OFPP_ANY)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        """
        receive flow_stat reply, then insert into database.
        entry is considered unique for cookie-datapath pair
        :param ev:
        """
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

            #check if the entry is already exists, if not create new entry
            if db.fidcheck(stat.cookie, ev.msg.datapath.id):
                current_th = (stat.byte_count - db.read_stat(stat.cookie, ev.msg.datapath.id))/monperiod
                #print "stat.byte_count "+ str(stat.byte_count)
                print str(stat.cookie) + " " + str(ev.msg.datapath.id) + " "     + str(current_th/1000) + "kbps"
                db.update_stat(stat.cookie, ev.msg.datapath.id, stat.byte_count, stat.packet_count)
                #insert throughput (kbps) based on current and previous bytes
                db.insert_throughput(stat.cookie, ev.msg.datapath.id, current_th/1000)
            else:
                db.insert_stat(stat.cookie, ev.msg.datapath.id, stat.byte_count, stat.packet_count)
                db.insert_throughput(stat.cookie, ev.msg.datapath.id, None)
