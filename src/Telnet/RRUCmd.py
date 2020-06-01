class RRUCmd:
    cmd_type_str = ['2.6GHz', '3.5GHz', '4.9GHz', 'ipaddr']

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
    def get_s_slot(cmdType):
        return ""

    @staticmethod
    def set_s_slot(cmdType, value):
        return ""

    @staticmethod
    def get_tdd_slot(cmdType):
        return ""

    @staticmethod
    def set_tdd_slot(cmdType, value):
        return ""

    @staticmethod
    def get_tx_gain(cmdType):
        return ""

    @staticmethod
    def set_tx_gain(cmdType, value):
        return ""

    @staticmethod
    def get_rx_gain(cmdType):
        return ""

    @staticmethod
    def set_rx_gain(cmdType, value):
        return ""

    @staticmethod
    def get_dpd(cmdType):
        return ""

    @staticmethod
    def set_dpd(cmdType, value):
        return ""


def main():
    cmd = RRUCmd.config_frequency('4.9G', 4900000000)

    print(cmd)


if __name__ == '__main__':
    main()
