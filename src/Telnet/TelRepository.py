from src.Telnet.Telnet import Telnet


class TelRepository:
    telnet_instance = Telnet()

    @staticmethod
    def connection_check():
        if TelRepository.telnet_instance.isTelnetLogined:
            if TelRepository.telnet_instance.tap():
                return True
            else:
                TelRepository.telnet_instance.terminate()
                return False
        else:
            return False
