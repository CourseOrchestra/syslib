#coding: utf-8
import unittest, random
from collections import OrderedDict
from any_functions import is_exist, Something
#from filter import as_default, recovery, filter_assembly


class Context:
    def __init__(self):
        self.inner_dict = {}

    def getData(self):
        return self.inner_dict


class FilterTest(unittest.TestCase):
    # setUp – подготовка прогона теста; вызывается перед каждым тестом.
    def setUp(self):
        print('Beginning of the unit testing')

    # tearDown – вызывается после того, как тест был запущен и результат записан. Метод запускается даже в случае
    # исключения (exception) в теле теста.
    def tearDown(self):
        print('This is the end')

    def test_run_once(self):
        self.is_exist_check()
        # self.recovery_test()
        self.headers_check()


    # Первая тестовая функция
    def is_exist_check(self):
            # Негативная проверка на корректность включённости ключа в словарь
            # Проверка на некорректные типы данных
            for i in [None, '1', 1, True, [], [1], {1}, (1, )]:
                self.assertEqual(is_exist(i, 1, None), None)
            # Логические значения
            self.assertEqual(is_exist({1: 2}, True, None), False)
            self.assertEqual(is_exist({0: 2}, False, None), False)
            self.assertEqual(is_exist({'': 2}, False, None), False)
            # Числа/строки
            self.assertEqual(is_exist({'1': ''}, 1), False)
            self.assertEqual(is_exist({'1': 2}, 1, None), False)
            self.assertEqual(is_exist({1: 2}, '1', None), False)
            self.assertEqual(is_exist({0: 2}, '', None), False)
            self.assertEqual(is_exist({0: 2}, 2, 2), False)
            # Проверка на корректность возвращённого значения при наличии значения
            self.assertEqual(is_exist({1: 2, '1': '2'}, 1, 2), True)
            self.assertEqual(is_exist({1: 2, '1': '2'}, 1, '2'), False)
            self.assertEqual(is_exist({1: 2, '1': '2'}, '1', '2'), True)
            self.assertEqual(is_exist({1: 2, '1': '2'}, 2, 1), False)
            # Тесты для путей в словарях
            smth = Something()
            self.assertEqual(is_exist({2: {2:3}, '1': '2'}, 2, {1:{2:smth}}), False)
            self.assertEqual(
                is_exist({'outer': {'inner1': {'inner2': {'default': ['we', 'have', 'it']}}
                                    , 'other': True, 'othertwo': 123, 'another': {1:2, 'oi': 'ne'}}},
                         'outer',
                         {'inner1': {'inner2': {'default': smth}}}
                ), True)
            self.assertEqual(
                is_exist({'outer': {'inner1': {'inner2': {'default': ['we', 'have', 'it']}}
                                    , 'other': True, 'othertwo': 123, 'another': {1:2, 'oi': 'ne'}}},
                         'outer',
                         {'inner1': {'inner2': smth}}, {'inor': smth}
                ), False)
            self.assertEqual(
                is_exist({'outer': {'inner1': {'inner2': {'default': ['we', 'have', 'it']}}
                                    , 'other': True, 'othertwo': 123, 'another': {1:2, 'oi': 'ne'}}},
                         'outer',
                         {'inner1': {'inner2': smth}}, {'inor'}
                ), False)
            self.assertEqual(
                is_exist({'outer': {'inner1': {'inner2': {'default': ['we', 'have', 'it']}}
                                    , 'other': True, 'othertwo': 123, 'another': {1:2, 'oi': 'ne'}}},
                         'outer',
                         {'inner1': {'inner2': smth}}, {'othertwo': 123}
                ), True)
            example_dict = {
                '@required' : 'false',
                '@style' : 'unbound',
                '@id' : 'period',
                'item' : {
                    '@id' : '',
                    '@name' : ''
                },
                'conditions' : {
                    'condition' : [{
                            '@value' : 'between',
                            '@label' : u'\u043c\u0435\u0436\u0434\u0443'
                        }
                    ]
                },
                '@tableName' : 'nsi.vw_aerodrome_cert',
                '@randint' : 0,
                '@type' : 'date',
                '@boolInput' : 'false',
                'selects' : {
                    'select' : []
                },
                '@minValue' : '01.01.2016',
                '@value' : '',
                '@label' : u'\u041f\u0435\u0440\u0438\u043e\u0434 \u0442\u0435\u043a\u0443\u0448\u0435\u0433\u043e \u0433\u043e\u0434\u0430',
                '@maxValue' : '07.09.2016',
                '@selector_data' : '',
                'default' : ['01.01.2016', '07.09.2016'],
                '@key' : 'view',
                '@current_condition' : 'between',
                'items' : {
                    'item' : []
                }
            }
            self.assertEqual(is_exist(example_dict, 'item', {'@id': smth} ), False)
            self.assertEqual(is_exist(example_dict, 'conditions', {'condition': smth} ), True)
            self.assertEqual(is_exist({'period': {'minValue': 90}}, 'period',
                                      {'minValue':smth, 'maxValue':smth}), False)
            self.assertEqual(is_exist({'period': {'minValue': 90, 'maxValue': 188}}, 'period',
                                      {'minValue':smth, 'maxValue':smth}), True)
            unbound_dict = {'strUnit': {'item': {u'@id': u'strUnits17', u'@name':
                u'\u0420\u0443\u043a\u043e\u0432\u043e\u0434\u0441\u0442\u0432\u043e'}, 'maxValue': u'', 'minValue': u'', 'condition': u'equal', 'text': u'', 'bool': False}, 'lastPeriod': {'item': {u'@id': u'', u'@name': u''}, 'maxValue': u'', 'minValue': u'', 'condition': u'equal', 'text': u'', 'bool': True}, 'tu': {'item': {u'@id': u'ogkn4', u'@name': u'\u0423\u0413\u0410\u041d \u041d\u041e\u0422\u0411 \u0426\u0424\u041e'}, 'maxValue': u'', 'minValue': u'', 'condition': u'equal', 'text': u'', 'bool': False}, 'date': {'item': {u'@id': u'', u'@name': u''}, 'maxValue': u'2016-09-13', 'minValue': u'2016-01-01', 'condition': u'between', 'text': u'', 'bool': False}}
            self.assertEqual(is_exist(unbound_dict, 'lastPeriod', {'bool': True}), True)

    # def generate_context_test(self):
    #     context = Context()
    #     num_of_fields = [1, 4, 7, 15, 50]
    #     current_filter_names = [
    #         {   rand_string(''.join([chr(x) for x in range(97, 123)]), random.randint(1, 14))
    #             for y in range(num)
    #         } for num in num_of_fields]
    #     print(generate_random_filter_data(current_filter_names))
    #     #self.assertEqual(recovery('context', 'add'), False)

    def headers_check(self):
        a = fill_example()
        self.assertEqual(a.return_header({'dichotomy': 'stool', 'punkt': False, 'posta': 783,
                                          'filtr_date': {'from': '2016-01-01', 'to': '2016-09-14'}}),
            u'Есть два стула; пункт не выполнен. Постановлений: 783. С 01.01.2016 по 14.09.2016')
        print('First is gone')
        self.assertEqual(a.return_header({'dichotomy': '', 'punkt': False, 'posta': 0,
                                          'filtr_date': ''}),
            u'Пункт не выполнен. Постановлений: 0.')
        print('Second is gone')
        self.assertEqual(a.return_header({'dichotomy': '', 'punkt': None, 'posta': None,
                                          'filtr_date': {'from': '2000-01-01', 'to': '2016-09-14'}}),
            u'С 01.01.2000 по 14.09.2016')
        print('Third is gone')
        self.assertEqual(a.return_header({'dichotomy': '', 'punkt': None, 'posta': None,
                                          'filtr_date': {'from': '', 'to': '2016-09-14'}}),
            u'По 14.09.2016')
        print('Fourth is gone')
        self.assertEqual(a.return_header({'dichotomy': '', 'punkt': None, 'posta': None,
                                          'filtr_date': {'from': '2000-01-01', 'to': ''}}),
            u'С 01.01.2000')
        print('Fifth is gone')


def fill_example():
    from filter_header import HeaderDict
    return HeaderDict(OrderedDict([
            ('dichotomy', {'data_type': 'text', 'label': u'есть два', 'values_to_header': {
                'stool': u'стула',  'tree': u'дерева'
                }, 'empty': ''}),
            ('punkt', {'data_type': 'bool', 'label': '', 'values_to_header': {
                True: u'пункт выполнен',  False: u'пункт не выполнен',
                }, 'empty': '\n', 'end': '.'}),
            ('posta', {'data_type': 'num', 'label': u'постановлений:', 'end': '.'}),
            ('filtr_date', {'data_type': 'date'})
        ]))


def rand_string(alphabet, size):
    return ''.join([random.choice(alphabet) for x in range(size)])


def generate_random_filter_data(field_names,
                                test_on=None      # Предполагаемая штуковина для того, чтобы тестить что-то конкретное
                                ):
    result_dict_list = []
    settings = { 'free': {True, False}, 'label': {'str'}, 'name': {'str'}, 'select': {'dict'},
                 'type': {'DATETIME', 'VARCHAR', 'NUMERIC', 'TEXT', 'INT', 'FLOAT', 'DATE', 'BOOLEAN'},
                 'selector': {True, False}, 'itemset': {True, False}, 'default': {'lst'},
                 'unbound': {True, False}, 'view': {True, False}, 'select_info': {'str'},
                 'especial_conds': {'equal', 'right', 'left', 'between'}, 'required': {True, False}}
    must_have_setting = {'label', 'name', 'view'}
    possible_sequences = [{'free', 'type', 'another'}, {'unbound', 'another'},
                          {'selector', 'select_info'}, {'select', 'type'},
                          {'itemset'}, {'default', 'another'}, {'especial_conds', 'another'},
                          {'required', 'another'}]
    for field in field_names:
        result_dict_list.append(
                {'label': field
                 }
        )

    return result_dict_list


if __name__ == "__main__":
    unittest.main()