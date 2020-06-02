import telnetlib
import logging
import time


class Telnet:
    timeout = 2  # Timeout Set as 2 secs
    delay = 0.6

    isTelnetOpened = False

    json_filename = 'Telnet'
    json_dict = ("host_ip", "username", "password")

    locked = False

    def __init__(self):
        self.tn = telnetlib.Telnet()
        self.warning = ''

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
            self.locked = True
            self.tn.open(host_ip, port=23)
        except:
            logging.warning('%sTelnet Open Failed' % host_ip)
            return False
        if username is not None:
            self.tn.read_until(b'login:', timeout=self.timeout)
            self.tn.write(username.encode('ascii') + b'\n')
        if password is not None:
            self.tn.read_until(b'Password:', timeout=self.timeout)
            self.tn.write(password.encode('ascii') + b'\n')

        time.sleep(self.delay)

        response = self.tn.read_very_eager().decode('ascii')
        self.locked = False
        '''Lock Out'''

        if 'incorrect' not in response:
            logging.info('%s Login Succeeded as %s' % host_ip % username)
            self.isTelnetOpened = True
            return True
        else:
            self.warning = response
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
        self.tn.write(command.encode('ascii') + b'\n')
        time.sleep(self.delay)
        response = self.tn.read_very_eager().decode('ascii')
        self.locked = False
        '''UnLock'''
        return response

    def get_warning(self):
        return self.warning
