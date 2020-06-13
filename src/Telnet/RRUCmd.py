class RRUCmd:

    DEBUG = -220

    FAIL = -1
    REBOOT = 0
    VERSION = 1
    GET_FREQUENCY = 2
    SET_FREQUENCY = 3
    GET_S_SLOT = 4
    SET_S_SLOT = 5
    GET_TDD_SLOT = 6
    SET_TDD_SLOT = 7
    GET_TX_ATTEN = 8
    SET_TX_ATTEN = 9
    GET_RX_GAIN = 10
    SET_RX_GAIN = 11

    GET_DL_OFFSET = 12
    SET_DL_OFFSET = 13
    GET_UL_OFFSET = 14
    SET_UL_OFFSET = 15

    GET_CPRI_STATUS = 20
    SET_CPRI = 21
    GET_CPRI_LOOP_MODE = 18
    SET_CPRI_LOOP_MODE = 19

    GET_AXI_REG = 20
    SET_AXI_REG = 21

    GET_AXI_OFFSET = 22
    SET_AXI_OFFSET = 23
    GET_IP_ADDR = 24
    SET_IP_ADDR = 25

    cmd_type_str = ['2.6GHz', '3.5GHz', '4.9GHz']
    ant_num = [2, 4, 4]

    slot_type_str = ['TDD', 'Special']

    @staticmethod
    def reboot():
        return ""

    @staticmethod
    def get_version():
        return ""

    # Get RRU frequency (HZ)
    @staticmethod
    def get_frequency(cmdType):
        return "rruAutoRun {cmdType} freq".format(cmdType=cmdType)

    # Set RRU frequency (HZ)
    @staticmethod
    def config_frequency(cmdType, value):
        return "rruAutoRun {cmdType} freq {value}".format(cmdType=cmdType, value=value)

    @staticmethod
    def get_s_slot(cmdType, antNum):
        return "rruAutoRun {cmdType} sSlot {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_s_slot(cmdType, antNum, value):
        return "rruAutoRun {cmdType} sSlot {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_tdd_slot(cmdType, antNum):
        return "rruAutoRun {cmdType} tddSlot {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_tdd_slot(cmdType, antNum, value):
        return "rruAutoRun {cmdType} tddSlot {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_tx_gain(cmdType, antNum):
        return "rruAutoRun {cmdType} txAtten {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_tx_gain(cmdType, antNum, value):
        return "rruAutoRun {cmdType} txAtten {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_rx_gain(cmdType, antNum):
        return "rruAutoRun {cmdType} rxGain {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_rx_gain(cmdType, antNum, value):
        return "rruAutoRun {cmdType} rxGain {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_dl_frame_offset(cmdType, antNum):
        return "rruAutoRun {cmdType} dlFrameOffset {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_dl_frame_offset(cmdType, antNum, value):
        return "rruAutoRun {cmdType} dlFrameOffset {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_ul_frame_offset(cmdType, antNum):
        return "rruAutoRun {cmdType} ulFrameOffset {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_ul_frame_offset(cmdType, antNum, value):
        return "rruAutoRun {cmdType} ulFrameOffset {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_link_delay(cmdType, antNum):
        return "rruAutoRun {cmdType} linkDelay {antNum}".format(cmdType=cmdType, antNum=antNum)

    @staticmethod
    def set_link_delay(cmdType, antNum, value):
        return "rruAutoRun {cmdType} linkDelay {antNum} {value}".format(cmdType=cmdType, antNum=antNum, value=value)

    @staticmethod
    def get_cpri(cmdType):
        return "rruAutoRun {cmdType} GetCpriStatus".format(cmdType=cmdType)

    @staticmethod
    def config_cpri(cmdType):
        return "rruAutoRun {cmdType} SetCpri".format(cmdType=cmdType)

    @staticmethod
    def get_cpri_loop_mode(cmdType):
        return "rruAutoRun {cmdType} cpriLoopMode".format(cmdType=cmdType)

    @staticmethod
    def config_cpri_loop_mode(cmdType, value):
        return "rruAutoRun {cmdType} cpriLoopMode {value}".format(cmdType=cmdType, value=value)

    @staticmethod
    def get_axis_offset(cmdType):
        return "rruAutoRun {cmdType} axi offsetAddr".format(cmdType=cmdType)

    @staticmethod
    def config_axis_offset(cmdType, value):
        return "rruAutoRun {cmdType} axi offsetAddr {value}".format(cmdType=cmdType, value=value)

    @staticmethod
    def get_axis_reg(cmdType, offset):
        return "rruAutoRun {cmdType} axi {offsetAddr}".format(cmdType=cmdType, offsetAddr=offset)

    @staticmethod
    def set_axis_reg(cmdType, change):
        return "rruAutoRun {cmdType} axi {change}".format(cmdType=cmdType, change=change)

    @staticmethod
    def change(offset, value):
        return "{offsetAddr} {value}".format(offsetAddr=offset, value=value)

    @staticmethod
    def get_ipaddr(cmdType):
        return "rruAutoRun {cmdType}".format(cmdType=cmdType)

    @staticmethod
    def config_ipaddr(cmdType, value):
        return "rruAutoRun {cmdType} {value}".format(cmdType=cmdType, value=value)


def main():
    cmd = RRUCmd.config_frequency('4.9G', 4900000000)

    print(cmd)


if __name__ == '__main__':
    main()
