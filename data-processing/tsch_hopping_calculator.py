
import json
from toolbox import get_all_files


# Todo use schedule class from toolbox
class NetSchedule:
    def __init__(self, slotframe_length, n_active_slots, hopping_seq,m_slot_map):
        self.hopping_sequence=hopping_seq
        self.slotframe_length = slotframe_length
        self.active_slots = n_active_slots
        self.mote_slot_map = m_slot_map

class TSCHopping:
    def __init__(self,full_path):
        print('Creating a TSCH hopper for %s' % full_path)

        foldername = full_path.split("/")[-1]
        folderpath = full_path[:-len(foldername)]
        files = get_all_files(folderpath,folders=[foldername])

        self.schedules = []
        for file in files:
            self.schedules.append(self.load_schedule(file))

        self.mote_net_map = {}
        for idx,schedule in enumerate(self.schedules):
            for a_slot in schedule.active_slots:
                mote_id = int(a_slot['address'].split(":")[-1][-2:],16)
                self.mote_net_map.__setitem__(mote_id,idx)

        #print('Schedules loaded')

    def load_schedule(self,file):
        #print("Loading schedule "+file)

        # read and parse config
        config = read_config(file)

        active_slots = config["active_slots"]
        numserialrx = config["numserialrx"]
        numslotoff = config["numslotoff"]

        slotframe_length = len(active_slots) + numserialrx + numslotoff

        hopping_sequence = config["hopping_seq"].split(',')

        mote_slot_map = {}
        parsed_active_slots = []
        for idx,slot in enumerate(active_slots):
            parsed_active_slots.append({'slot_offset': slot["slotOffset"], 'channel_offset': slot["channelOffset"], 'address': slot["address"]})
            mote_id = int(slot['address'].split(":")[-1][-2:], 16)
            mote_slot_map.__setitem__(mote_id,idx)

        #app_enabled = config["app_enabled"]
        #app_type = config["app_type"]
        #app_dest_addr = config["app_dest_addr"]

        return NetSchedule(slotframe_length,parsed_active_slots,hopping_sequence,mote_slot_map)

    def find_mote_info(self, mote_id):
        target_schedule = self.schedules[self.mote_net_map.get(mote_id)]
        hopping_sequence = target_schedule.hopping_sequence
        mote_active_slot = target_schedule.active_slots[target_schedule.mote_slot_map.get(mote_id)]
        channel_offset = mote_active_slot['channel_offset']
        return hopping_sequence, channel_offset

    def calculate_frequency(self, mote_id, asn):
        hopping_sequence,channel_offset = self.find_mote_info(mote_id)
        asn_offset = asn % 16
        return int(hopping_sequence[(asn_offset+channel_offset)%16])+11

    def calculate_dropped_frequency(self, mote_id, n_frames_ago, asn_last):
        target_schedule = self.schedules[self.mote_net_map.get(mote_id)]
        return self.calculate_frequency(mote_id, asn_last-n_frames_ago*target_schedule.slotframe_length)


def read_config(fname):
    """
    Read configuration file as json object
    :param fname: file to read from
    :return: list of dicts
    """

    with open(fname) as data_file:
        data = json.load(data_file)

    # pprint(data)

    return data

if __name__ == '__main__':
    for i in range(1, 2):

        foldername="../../WHData/Data/Schedules/schedules_lkngolden"
        a = TSCHopping(foldername)

        mote_id = int('1a',16)
        ASN = 1000
        freq = a.calculate_frequency(mote_id,ASN)

        print("The frequency used by %d to transmit in ASN %d is %d " % (mote_id,ASN,freq))