import re

from src.Telnet.RRUCmd import RRUCmd
from src.Tool.ValidCheck import ValidCheck


class RespFilter:
    FREQUENCY_ASSERTION = 'freq:'
    TX_ATTEN_ASSERTION = 'txAtten'
    RX_GAIN_ASSERTION = 'rxGain'
    TDD_SLOT_ASSERTION = 'tddSlot'
    S_SLOT_ASSERTION = 'sSlot'
    UL_OFFSET_ASSERTION = 'UlFrameOffset'
    DL_OFFSET_ASSERTION = 'dlFrameOffset'

    IP_ADDR_ASSERTION = 'ipaddr:'
    AXI_OFFSET_ASSERTION = 'axi reg '

    CPRI_LOOP_MODE_ASSERTION = 'cpriLoopMode'

    CPRI_STATUS_ASSERTION = 'CPRI status is'
    CPRI_CONFIG_OK = 'CPRI config complete'
    CMD_OK = 'CMD OK'
    CMD_FAIL = 'CMD FAILED'

    @staticmethod
    def resp_check(resp):
        if resp is None:
            return False
        if RespFilter.CMD_FAIL not in resp:
            return True
        else:
            return False

    @staticmethod
    def value_filter(resp, ast: str):
        if RespFilter.resp_check(resp):
            return re.search(r'(?<=' + ast + r')\d+(\.\d+)?', resp)
        else:
            return None

    @staticmethod
    def value_filter_with_ant(resp, ast: str, antNum: int):
        if RespFilter.resp_check(resp):
            return re.search(r'(?<=' + ast + str(antNum) + r':' + r')\d+(\.\d+)?', resp)
        else:
            return None

    @staticmethod
    def hex_value_filter(resp, ast: str):
        if RespFilter.resp_check(resp):
            return re.search(r'(?<=' + ast + r')0[xX][0-9a-fA-F]+:0[xX][0-9a-fA-F]+', resp)
        else:
            return None

    @staticmethod
    def word_value_filter(resp, ast: str):
        if RespFilter.resp_check(resp):
            return re.search(r'(?<=' + ast + r')( \w+)+', resp)
        else:
            return None

    @staticmethod
    def axi_read_filter(resp):
        return re.search(r'(?<=read axi reg )0[xX][0-9a-fA-F]{8}:0[xX][0-9a-fA-F]{8}', resp)

    @staticmethod
    def ipaddr_read_filter(resp):
        return re.search(r'(?<=The ipaddr is \[)'
                         r'((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}', resp)

    @staticmethod
    def trim_cpri_status(resp: str):
        begin = resp.find(RespFilter.CPRI_STATUS_ASSERTION)
        end = resp.find(RespFilter.CMD_OK)
        if begin != -1 and end != -1:
            begin += len(RespFilter.CPRI_STATUS_ASSERTION)
            res = resp[begin: end].replace("\n", "")
            return res.replace("\r", "").upper()
        else:
            return None

    @staticmethod
    def trim(resp: str):
        resp = resp.replace("\n\r", " ")
        resp = resp.replace("\r\n", " ")
        resp = resp.replace("\r", " ")
        resp = resp.replace("\n", " ")
        return resp


def main():
    text = "txAtten1:36000"

    res = RespFilter.value_filter_with_ant(text, RespFilter.TX_ATTEN_ASSERTION, 0)

    if res is not None:
        print(str(res.group()))
    else:
        print('Failed')

    i = 0
    if res is None:
        if 0 == i:
            i += 1
        while res is None and i < 4:
            res = RespFilter.value_filter_with_ant(text, RespFilter.TX_ATTEN_ASSERTION, i)
            i += 1
        i -= 1
    else:
        i = 0
    if res is not None:
        print(str(res.group()))
        res = ValidCheck.transfer_attenuation(res.group(), RRUCmd.GET_TX_ATTEN)
        print(res)
        print(i)


if __name__ == '__main__':
    main()
