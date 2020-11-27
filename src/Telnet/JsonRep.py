import json

from src.Telnet.Telnet import Telnet


def save_by_json(data_in_json):
    _write_json(Telnet.json_filename, data_in_json)


def read_json(file_name):
    with open('../JSON/' + file_name + '.json', 'r') as f:
        return json.load(f)


def _write_json(file_name, data):
    with open('../JSON/' + file_name + '.json', 'w') as f:
        json.dump(data, f)


def login_by_json(self):
    data_in_json = read_json(self.json_filename)
    return self.login(data_in_json['host_ip'], data_in_json['username'], data_in_json['password'])


class AxiJson:
    FILENAME = "AXI"

    AXI_ADDR = "ADDR"
    AXI_REG = "REG"

    @staticmethod
    def save_axi(data_in_json):
        _write_json(AxiJson.FILENAME, data_in_json)

    @staticmethod
    def read_axi():
        try:
            return read_json(AxiJson.FILENAME)
        except:
            return []
