import re

from src.Telnet.RRUCmd import RRUCmd


class ValidCheck:
    # 195-255，步进 0.5
    GAIN_RE = r"(^(1[9][5-9]|2[0-4][0-9]|25[0-4])(\.5)?)|(^(255)(\.0)?)|(^(1[9][5-9]|2[0-4][0-9]|25[0-4])(\.0)?)"
    # IPV4
    IPADDR_RE = r"((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})(\.((2(5[0-5]|[0-4]\d))|[0-1]?\d{1,2})){3}"
    # 非负浮点数
    NON_NEGATIVE_FLOAT_RE = r"^\d+(\.\d+)?$"
    # 非正浮点数
    NON_POSITIVE_FLOAT_RE = r"^((-\d+(\.\d+)?)|(0+(\.0+)?))$"
    # 浮点数
    FLOAT_RE = r"^(-?\d+)(\.\d+)?$"
    # HEX
    HEX_RE = r"^0[xX][0-9a-fA-F]+$"

    @staticmethod
    def is_number(s):
        try:
            float(s)
            return True
        except ValueError:
            pass

        try:
            import unicodedata
            unicodedata.numeric(s)
            return True
        except (TypeError, ValueError):
            pass

        return False

    @staticmethod
    def reg_format(s_value: str):
        try:
            n = int(s_value, 16)
            return '0x{:08x}'.format(n)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def freq(option: str, s_value: str):
        """Check validity of Frequency input
        :option:    CMDType 0 for 2.6 GHz, 1 for 3.5 GHz, 2 for 4,9 GHz
        :s_value:   frequency as str

        :return:    True or False
        """
        if s_value.isdigit():
            n_value = int(s_value)
            if option == RRUCmd.cmd_type_str[0]:
                return 2565000000 <= n_value <= 2625000000
            elif option == RRUCmd.cmd_type_str[1]:
                return 3450000000 <= n_value <= 3550000000
            elif option == RRUCmd.cmd_type_str[2]:
                return 4850000000 <= n_value <= 4950000000
        else:
            return False

    @staticmethod
    def transfer_attenuation(s_value: str, case: int):
        """Unit Convert
        GUI uses dB as basic unit
        """
        try:
            if case == RRUCmd.SET_TX_ATTEN:
                # dB -> mdB
                return str(int(float(s_value) * -1000))
            elif case == RRUCmd.SET_RX_GAIN:
                # dB -> RRU Dimension
                return str(float(s_value) * 2 + 255)
            elif case == RRUCmd.GET_TX_ATTEN:
                # mdB -> dB
                if float(s_value) == 0:
                    return "0.0"
                else:
                    return str(float(s_value) / -1000)
            elif case == RRUCmd.GET_RX_GAIN:
                # RRU Dimension -> dB
                return str((float(s_value) - 255) / 2)
        except ValueError:
            return None

    @staticmethod
    def atten(s_value: str):
        """Check validity of tx attenuation input
        :return:    True or False
        """
        if s_value is None:
            return False
        elif s_value.isdigit():
            n_value = int(s_value)
            return n_value <= 41950
        else:
            return False

    @staticmethod
    def filter(s_re: str, s_value: str):
        """Filter using re
            :s_re:      re expression
            :s_value:   value as str

            :return:    math group
                        or none    when cannot match
        """
        if s_value is None:
            return None
        else:
            return re.match(s_re, s_value)

    @staticmethod
    def addr_transfer(s_value, case):
        if case == RRUCmd.GET_AXI_REG:
            # Offset Addr -> Addr
            return hex(int(s_value, 16) + 0x40000000)
        elif case == RRUCmd.SET_AXI_REG:
            # Addr -> Offset Addr
            return hex(int(s_value, 16) - 0x40000000)


def main():
    rxGain2set = "02222222222201"
    if True:
        # Transfer Unit
        match = ValidCheck.reg_format(rxGain2set)
    if match is not None:
        print(match)
    else:
        print("Failed")


if __name__ == '__main__':
    main()
