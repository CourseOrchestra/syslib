#coding: utf-8
import unittest, random
from any_functions import is_exist
from filter import as_default, recovery, filter_assembly


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
        self.is_exist_fun_test()
        self.recovery_test()

    # Первая тестовая функция
    def is_exist_fun_test(self):
            # Негативная проверка на корректность включённости ключа в словарь
            # Проверка на некорректные типы данных
            for i in [None, '1', 1, True, [], [1], {1}, (1, )]:
                self.assertEqual(is_exist(i, 1, None), None)
            # Логические значения
            self.assertEqual(is_exist({1: 2}, True, None), False)
            self.assertEqual(is_exist({0: 2}, False, None), False)
            self.assertEqual(is_exist({'': 2}, False, None), False)
            # Числа/строки
            self.assertEqual(is_exist({'1': 2}, 1, None), False)
            self.assertEqual(is_exist({1: 2}, '1', None), False)
            self.assertEqual(is_exist({0: 2}, '', None), False)
            self.assertEqual(is_exist({0: 2}, 2, 2), False)
            # Проверка на корректность возвращённого значения при наличии значения
            self.assertEqual(is_exist({1: 2, '1': '2'}, 1, 2), True)
            self.assertEqual(is_exist({1: 2, '1': '2'}, 1, '2'), False)
            self.assertEqual(is_exist({1: 2, '1': '2'}, '1', '2'), True)
            self.assertEqual(is_exist({1: 2, '1': '2'}, 2, 1), False)

    def generate_context_test(self):
        context = Context()
        num_of_fields = [1, 4, 7, 15, 50]
        current_filter_names = [
            {   rand_string(''.join([chr(x) for x in range(97, 123)]), random.randint(1, 14))
                for y in range(num)
            } for num in num_of_fields]
        print(generate_random_filter_data(current_filter_names))
        #self.assertEqual(recovery('context', 'add'), False)


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