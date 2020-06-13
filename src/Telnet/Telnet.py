import telnetlib
import logging
import time

return_symbol = b'\r'


class Telnet:
    timeout = 4  # Timeout Set as 4 secs
    delay = 0.5

    isTelnetOpened = False
    isTelnetLogined = False
    loginedUserName = ''

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
                            format='[%(asctime)s-%(filename)s-%(funcName)s-%(levelname)s:%(message)s]',
                            level=logging.DEBUG, filemode='a', datefmt='%Y-%m-%d %I:%M:%S %p')

    def lock_check(self):
        while self.locked:
            time.sleep(0.1)

    def login(self, host_ip, username, password):
        # Logout first if telnet opened already
        if self.isTelnetLogined:
            self.lock_check()
            self.logout()
        try:
            '''Lock'''
            print('Try to open Telnet')
            logging.debug('Try to open Telnet %s' % host_ip)
            self.locked = True
            self.tn.open(host_ip, port=23, timeout=self.timeout)
            self.isTelnetOpened = True
            logging.debug('%s Telnet Opened' % host_ip)
        except Exception as argument:
            logging.warning('%s , Telnet Open Failed' % argument)
            self.warning = argument
            return False

        if username is not None and len(username) != 0:
            logging.debug('Try to login as %s' % username)
            self.tn.read_until(b'login:', timeout=self.timeout)
            self.tn.write(username.encode('ascii') + b'\r')
            logging.debug('Username input')
        else:
            self.locked = False
            return False

        if password is not None and len(password) != 0:
            logging.debug('Try to input password')
            self.tn.read_until(b'password:', timeout=self.timeout)
            logging.debug('Find assertion for password')
            if len(password) == 0:
                self.tn.write(b'\r')
            else:
                self.tn.write(password.encode('ascii') + return_symbol)
            logging.debug('Password input:  %s' % password)
        else:
            self.locked = False
            return False

        time.sleep(self.delay)

        result = self._get_result()

        # response = self.tn.read_very_eager().decode('ascii')
        logging.debug(result)
        self.locked = False
        '''Lock Out'''

        if username in result:
            logging.info('%s Login Succeeded' % host_ip)
            self.isTelnetLogined = True
            self.loginedUserName = username
            return True
        elif 'incorrect' in result or 'Failed' in result:
            self.warning = result
            logging.warning('%s Login Failed' % host_ip)
            logging.warning(result)
            if self.isTelnetOpened:
                self.tn.close()
            return False
        else:
            self.warning = result
            logging.warning('%s Login Failed' % host_ip)
            logging.error(result)
            if self.isTelnetOpened:
                self.tn.close()
            return False

    def logout(self):
        self.lock_check()
        try:
            '''Lock'''
            self.locked = True
            self.tn.write("exit".encode('ascii') + return_symbol)
            logging.info("Logged out from %s" % self.loginedUserName)
        finally:
            self.locked = False
            '''UnLock'''
            self.terminate()

    def execute_command(self, command):
        """Send command and get response
        :return:    None    when Exception is thrown
                    resp    when response successfully received through telnet
        """
        self.lock_check()
        '''Lock'''
        self.locked = True
        response = ''
        try:
            self.tn.write(command.encode('ascii') + return_symbol)
            logging.info("send " + command)
            time.sleep(self.delay)
            response = self._get_result()
            logging.info("recv " + response)
        except Exception as argument:
            logging.error(argument)
            response = None
        finally:
            self.locked = False
            '''UnLock'''
            return response

    def tap(self):
        """Send a return symbol to check whether the connection and login is live
        """
        if self.isTelnetLogined:
            result = False

            try:
                self.lock_check()
                '''Lock'''
                self.locked = True
                logging.debug('Tap Starts Here')

                self.tn.write(return_symbol)
                time.sleep(self.delay)
                response = self._get_result()

                if self.loginedUserName in response:
                    logging.info('Login alive')
                    result = True
                else:
                    logging.info('Login dead')
                    result = False
            except Exception as argument:
                logging.warning(argument)
                result = False
            finally:
                self.locked = False
                '''UnLock'''
                return result

        else:
            logging.info('Not login yet')
            return False

    def terminate(self):
        try:
            self.tn.close()
        finally:
            self.isTelnetLogined = False
            self.isTelnetOpened = False

    def get_warning(self):
        return self.warning

    def _get_result(self):
        result = str()
        a = []
        while True:
            b, c, d = self.tn.expect(a, timeout=self.delay)
            result = result + str(d, encoding="gbk")
            if b == 0:
                self.tn.write(r' ')
            else:
                break
        return result
