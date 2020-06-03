import telnetlib
import logging
import time


class Telnet:
    timeout = 2  # Timeout Set as 2 secs
    delay = 2

    isTelnetOpened = False

    json_filename = 'Telnet'
    json_dict = ("host_ip", "username", "password")

    locked = False

    def __init__(self):
        self.tn = telnetlib.Telnet()
        self.tn.set_debuglevel(2)
        self.set_logger()
        self.warning = ''

    @staticmethod
    def set_logger():
        logging.basicConfig(filename='../log/' + __name__ + '.log',
                            format='[%(asctime)s-%(filename)s-%(levelname)s:%(message)s]', level=logging.DEBUG,
                            filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    def lock_check(self):
        while self.locked:
            time.sleep(0.05)

    def login(self, host_ip, username, password):
        # Logout first if telnet opened already
        if self.isTelnetOpened:
            self.lock_check()
            self.logout()
        try:
            '''Lock'''
            print('Try to open Telnet')
            logging.debug('Try to open Telnet %s' % host_ip)
            self.locked = True
            self.tn.open(host_ip, port=23)
            logging.debug('%s Telnet Opened' % host_ip)
        except:
            logging.warning('%s Telnet Open Failed' % host_ip)
            self.warning = 'Telnet Open Failed'
            return False

        if username is not None:
            logging.debug('Try to login as %s' % username)
            self.tn.read_until(b'login:', timeout=5)
            self.tn.write(username.encode('ascii') + b'\r')
            logging.debug('Username input')

        if password is not None:
            logging.debug('Try to input password')
            self.tn.read_until(b'password:', timeout=self.timeout)
            logging.debug('Find assertion for password')
            if len(password) == 0:
                self.tn.write(b'\r')
            else:
                self.tn.write(password.encode('ascii') + b'\r')
            logging.debug('Password input:  %s' % password)

        time.sleep(self.delay)

        result = self.get_result()

        # response = self.tn.read_very_eager().decode('ascii')
        logging.debug(result)
        self.locked = False
        '''Lock Out'''

        if 'incorrect' not in result and 'Failed' not in result:
            logging.info('Login Succeeded')
            self.isTelnetOpened = True
            return True
        else:
            self.warning = result
            logging.warning('%s Login Failed' % host_ip)
            self.isTelnetOpened = False
            return False

    def logout(self):
        self.lock_check()
        '''Lock'''
        self.locked = True
        self.tn.write(b"exit\n")
        self.locked = False
        '''UnLock'''
        self.isTelnetOpened = False

    def execute_command(self, command):
        self.lock_check()
        '''Lock'''
        self.locked = True
        self.tn.write(command.encode('ascii') + b'\r')
        logging.info("send " + command)
        time.sleep(self.delay)
        response = self.get_result()
        logging.info("recv " + response)
        self.locked = False
        '''UnLock'''
        return response

    def get_warning(self):
        return self.warning

    def get_result(self):
        result = str()
        a = []
        while True:
            b, c, d = self.tn.expect(a, timeout=1)
            result = result + str(d, encoding="gbk")
            if b == 0:
                self.tn.write(r' ')
            else:
                break
        return result
