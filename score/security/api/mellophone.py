# coding: utf-8
'''
Created on 20 мар. 2017 г.

@author: m.prudyvus
'''
from __future__ import unicode_literals

from java.io import BufferedReader, InputStreamReader
from java.lang import StringBuffer
from java.net import URL, HttpURLConnection


class SecurityMellophoneException(Exception):
    """Исключение при ошибках работы с Мелофоном. 
    """

    def __init__(self, code, msg):
        super(self.__class__, self).__init__(msg)
        self.code = code

    def critical(self):
        return u"{!.3i}: {}".format(self.code, self.message)


def get_url_string(java_net_url):
    result = java_net_url.getProtocol() + '://'
    result += java_net_url.getAuthority()
    result += java_net_url.getPath()
    result += java_net_url.getQuery()

    return result


class Mellophone(object):

    def __init__(self, base_url, session_id=None):
        """
        @param base_url: адрес меллофона
        """
        self.session_id = session_id
        self._base_url = base_url

    def _send_request(self, url):
        url = self._base_url + url
        conn = None
        try:
            conn = self._get_connection(url)
            conn.setRequestMethod('GET')
            conn.connect()
            if conn.getResponseCode() == HttpURLConnection.HTTP_OK:  # Если запрос обработался хорошо
                return
            else:
                self._on_error(conn)
        finally:
            if conn:
                conn.disconnect()

    def login(self, login, password, ses_id=None, gp=None):
        """Выполняет регистрацию с помощью мелофона.

        При регистрации сгенерированный ИД сессии сохраняется в Cookie и используется для всех
        последующих запросов с помощью созданного объекта Mellohone. Повторный вызов login() с 
        пустым ses_id перезапишет текущий Cookie. 

        Параметры:
            - login (string) - имя пользователя
            - password (string) - пароль в открытом виде
            - ses_id (string) - идентифиатор сессии
            - gp (sring) - группа провайдеров
        """
        if not ses_id:
            ses_id = self.session_id

        url = 'login?&sesid={}&login={}&pwd={}'.format(ses_id, login, password)

        if gp:
            url += '&gp={}'.format(gp)

        self._sendRequest(url)

    def logout(self, ses_id):
        if not ses_id:
            ses_id = self.session_id
        url = 'login?&sesid={}'.format(ses_id)

        self.sendRequest(url)

    def check_credentials(self, login, password):
        #         if not self._cookie:
        #             raise ValueError(self._ERROR_COOKIE_MSG.format('check_credentials'))
        url = 'checkcredentials?login={}&pwd={}'.format(login, password)

        self._sendRequest(url)

    def _get_connection(self, url):
        server = URL(url)

        url_conn = server.openConnection()  # Подключаемся

        return url_conn

    def _on_error(self, url_conn):
        get_input_stream = url_conn.getResponseCode() < HttpURLConnection.HTTP_BAD_REQUEST
        if get_input_stream:
            in_stream = url_conn.getInputStream()
        else:
            in_stream = url_conn.getErrorStream()

        in_stream = BufferedReader(InputStreamReader(in_stream, 'utf-8'))

        response = StringBuffer()
        while True:
            inputLine = in_stream.readLine()
            if not inputLine:
                break
            response.append(inputLine)
        response = response.toString()

        in_stream.close()

        print "_melophone_request:\n\turl: {}\n\t:error: {}".format(get_url_string(url_conn.getURL()), response).encode('utf-8')

        raise SecurityMellophoneException(7, response)

    def import_gp(self):
        url = '/importgroupsproviders'
        self._send_request(url)
