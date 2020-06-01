import re


class RespFilter:
    FREQUENCY_ASSERTION = 'freq:'

    @staticmethod
    def resp_check(resp):
        if 'CMD FAILED' not in resp:
            return True
        else:
            return False

    @staticmethod
    def value_filter(resp, ast: str):
        if RespFilter.resp_check(resp):
            return re.search(r'(?<=' + ast + r')\d+', resp)
        else:
            return None


def main():
    text = "freq:4900000Hz\rCMD OK"

    res = RespFilter.value_filter(text, RespFilter.FREQUENCY_ASSERTION)

    if res is not None:
        print(str(res.group()))
    else:
        print('Failed')


if __name__ == '__main__':
    main()
