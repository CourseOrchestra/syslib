# coding: UTF-8
u'''
Created 28.02.2016 by s.gavrilov
'''
from array import array
from datetime import datetime
from java.io import FileOutputStream, BufferedInputStream, FileInputStream
import os

from common.grainssettings import SettingsManager
from common.numbersseries.getNextNo import getNextNoOfSeries
from fileRepository._fileRepository_orm import fileCounterCursor, \
    fileCursor, fileVersionCursor
from ru.curs.celesta import CelestaException


try:
    from ru.curs.showcase.core.jython import JythonDownloadResult
except:
    from ru.curs.celesta.showcase import JythonDownloadResult


def putFile(context, native_filename, stream_input, current_cluster_num=1,
            rewritten_file_id=None, uploadVersioning=None):
    '''
    native_filename - имя загружаемого файла,
    stream_input - входящий java поток,
    current_cluster_num - номер кластера, в который следует положить файл,
    rewritten_file_id - если передаётся id файла, то его переписываем,
    uploadVersioning - если True, предыдущая версия файла не перезаписывается.
    Происходит запись файла в кластер, путь к которому должен быть указан в
    grainSettings.xml -> <grain name="fileRepository"><clusterPath>
    Плюс, происходит запись в БД о файле.
    '''

    file_version_cursor = fileVersionCursor(context)
    file_cursor = fileCursor(context)
    file_count_cursor = fileCounterCursor(context)

    '''Временная проверка на кластера существование'''
    try:
        if not file_count_cursor.tryGet(int(current_cluster_num)):
            context.error(u'В таблице кластеров переданный id не содержится.')
    except (TypeError, ValueError):
        context.error(
            u'Передаваемый номер кластера представлен недопустимым типом (не число).')
    '''Имена для серий номеров.'''
    file_NS_name = 'filesNS'
    file_vers_NS_name = 'fileVerNS'
    '''Путь к создающемуся файлу, имя файла на сервере,
    словарь с данными из generalSettings'''
    path_to, digit_file_name, amount_and_nest = getPathToFile(
        context, current_cluster_num)
    file_multiplicator = len(str(amount_and_nest['filesAmount']))

    if not rewritten_file_id:
        '''
        Создаём запись под новый файл в обеих таблицах.
        '''
        file_cursor.id = getNextNoOfSeries(context, file_NS_name)
        file_cursor.name = native_filename
        file_cursor.uploadVersioning = uploadVersioning or None
    else:
        '''
        Если записываем новую версию существующего файла:
        Либо поддерживаем uploadVersioning и записываем файл,
        иначе удаляем последнюю версию существующего файла и
        добавляем в таблицу fileVersion запись о новой последней версии.
        '''
        if not file_cursor.tryGet(rewritten_file_id):
            context.error(
                u'Id файла, который надо перезаписать, не найден в базе.')
        file_cursor.name = native_filename
        file_version_cursor.setRange('fileId', '%s' % rewritten_file_id)
        file_version_cursor.setRange("exist", True)
        '''Если не поддерживается сохранение предыдущей версии'''
        if not file_cursor.uploadVersioning:
            '''Ищем данный последний файл.'''
            if file_version_cursor.tryFirst():
                path_to_dying_file = throughListToPath(
                    amount_and_nest['clusterPath'],
                    file_version_cursor.fileName,
                    file_multiplicator)  # Получаем путь из имени файла
                try:
                    os.remove(path_to_dying_file)
                except OSError:
                    context.error(u'Ошибочный путь к файлу внутри системы.')
            '''Предыдущая версия удаляется => не существует'''
            for file_version in file_version_cursor.iterate():
                if file_version.exist:
                    file_version.exist = 0
                    file_version.update()

    file_version_cursor.id = getNextNoOfSeries(context, file_vers_NS_name)
    file_version_cursor.fileId = file_cursor.id
    # Добавить функцию распределения кластеров как появятся
    file_version_cursor.clasterId = 1
    file_version_cursor.fileName = digit_file_name
    # file_version_cursor.versionMajor =
    # file_version_cursor.versionMinor =
    file_version_cursor.exist = 1
    file_version_cursor.timestamp = datetime.today()

    '''Обновление/Добавление кластера в таблице fileCounter.'''
    refresher = 1
    for file_counter in file_count_cursor.iterate():
        if file_counter.clasterId == amount_and_nest['clusterNumber']:
            file_counter.latestFileName = digit_file_name
            file_counter.update()
            refresher = 0

    if refresher:
        file_count_cursor.clasterId = amount_and_nest['clusterNumber']
        file_count_cursor.latestFileName = digit_file_name
        file_count_cursor.insert()

    '''Собственно, запись файла.'''
    fileToWrite = FileOutputStream(path_to)
    size_of_file = 0
    buffer_stream = BufferedInputStream(stream_input, 4096)
    d = array('b', [0 for i in xrange(4096)])

    try:
        c = buffer_stream.read(d, 0, 4096)
        while c != -1:
            fileToWrite.write(d[:c])
            size_of_file += 1
            c = buffer_stream.read(d, 0, 4096)
    finally:
        stream_input.close()
        fileToWrite.close()

    if size_of_file < 8:
        repairNullString(path_to)
    '''3апись в БД в случае, если при загрузке не произошла ошибка'''
    if not rewritten_file_id:
        file_cursor.insert()
    else:
        file_cursor.update()
    file_version_cursor.insert()

    return file_version_cursor.id


def getPathToFile(context, current_cluster_num):
    '''
    Функция, которая дополняет иерархию внутри кластера
    до заданной в grainssettings, и возвращает имя текущего файла
    '''
    """Получаем словарь с настройками данного кластера"""
    amount_and_nest = pullGrainSettings(context, current_cluster_num)
    '''Проверяем, существует ли данный кластер. Если нет, то создаём.'''
    try:
        if not os.path.exists(amount_and_nest['clusterPath']):
            os.makedirs(amount_and_nest['clusterPath'])
    except OSError:
        context.error(u'Указывайте адрес кластера в существующей директории.')

    # Получаем количество разрядов под общее число файлов(папок) в папке
    file_multiplicator = len(str(amount_and_nest['filesAmount']))
    temp_path = amount_and_nest['clusterPath']

    files_version_cursor = fileVersionCursor(context)
    files_version_cursor.orderBy('fileName')
    files_version_cursor.tryLast()

    '''Проверка, была ли информация в grainssettings изменена.'''
    if files_version_cursor.fileName:
        aspect_ratio = len(files_version_cursor.fileName) // file_multiplicator
        if aspect_ratio != amount_and_nest['nestingSize'] + 1:
            context.error(u'Данные в grainssettings были изменены \
            в процессе эксплуатации БД. \
            Чтобы дальнейшая работа была корректной, \
            следует очистить таблицы fileVersion и file.')

    if files_version_cursor.fileName:
        ''' Следующая функция создаёт следующий по порядку файл и
        прописывает(создает) для него путь '''
        path_to_file = createDirectories(
            temp_path, files_version_cursor.fileName,
            file_multiplicator, amount_and_nest['filesAmount'])
        file_name = os.path.basename(path_to_file)   # Вытаскиваем имя файла
        if not path_to_file:
            context.error(
                u'В текущих кластерах слишком много файлов,\
                создайте новый кластер.')
    else:
        import shutil
        root, dirs, files = os.walk(temp_path).next()
        '''Чистим директорию от посторонних объектов.'''
        try:
            for directory in dirs:
                shutil.rmtree(os.path.join(root, directory))
            for fil in files:
                os.remove(os.path.join(root, fil))
        except:
            context.error(
                u'Недостаточно прав для очистки выбранной под кластер папки. \
                Выберите другой адрес.')
        '''Создаем путь до первого файла в кластере.'''
        i = 0
        while i < amount_and_nest['nestingSize']:
            # Составляем путь до папки, где будут лежать файлa
            temp_path += '\\%s1' % ('0' * (file_multiplicator - 1))
            os.mkdir(os.path.abspath(temp_path))
            i += 1

        # Составляем имя первого файла в кластере
        file_name = ('0' * (file_multiplicator - 1) + '1') * \
            (amount_and_nest['nestingSize'] + 1)
        path_to_file = os.path.join(temp_path, file_name)

    return path_to_file, file_name, amount_and_nest


def createDirectories(path, file_name, file_multiplicator, restriction):
    '''
    Функция принимает path : путь к текущему кластеру,
    file_name : имя последнего добавленного файла,
    file_multiplicator : количество вложенных папок,
    restriction : максимально допустимое количество объектов в каждой папке
    Возвращает полный путь до ещё не созданного файла, либо None,
    если внутри кластера нет места
    '''

    """Получаем список вида
    [1 : первая вложенная в кластер директория,
     2 : вторая ...,
     3 : порядковый номер файла ]"""
    dir_names = nameToPathList(file_name, file_multiplicator)

    dir_names = [int(x) for x in dir_names]
    dir_names[-1] += 1  # Создаём имя для следующего файла
    flex_dir_names = []
    jump = 0
    '''Цикл проверяет новосозданный путь к файлу на превышения,
    указанные в restriction (grainssettings).'''
    for index, dir_name in enumerate(dir_names[::-1]):
        current_name = dir_name + jump  # Текущее "имя" файла/директории
        if current_name > restriction:
            '''При выполнении кластер заполнен.'''
            if index == file_multiplicator:
                return None
            '''Создание имени новой директории или файла, без разницы.'''
            flex_dir_names.append(1)
            jump = 1
        else:
            flex_dir_names.append(current_name)
            jump = 0

    dir_names = flex_dir_names[::-1]
    file_name = ''
    '''Создаём корректный путь к размещаемому файлу.'''
    dir_names = [str(x).zfill(file_multiplicator) for x in dir_names]
    for dir_name in dir_names[:-1]:
        path = os.path.join(path, dir_name)
        if not os.path.isdir(path):
            os.mkdir(path)
    '''Составляем имя файла.'''
    file_name = ''.join(dir_names)
    return os.path.join(path, file_name)


def nameToPathList(file_name, file_multiplicator):
    dir_names = []
    '''Цикл составляет из имени файла путь к нему от кластерной папки.'''
    for i in xrange(file_multiplicator):
        dir_names.append(
            file_name[i * file_multiplicator:  (i + 1) * file_multiplicator]
        )

    return dir_names


def totalAnnihilation(context, file_id):
    '''
    Удаление файла из репозитория и БД вместе с логами.
    '''
    file_cursor = fileCursor(context)
    file_ver_cursor = fileVersionCursor(context)
    grains_settings_XML = SettingsManager(context)

    if not file_cursor.tryGet(file_id):
        context.error(
            u'Записи о данном файле в таблице files не существует.')

    file_ver_cursor.setRange('fileId', file_id)
    file_ver_cursor.first()

    for index, cur_num in enumerate(grains_settings_XML.getGrainSettings(
            'clusterPath/cluster/@number', 'fileRepository')):
        if cur_num == str(file_ver_cursor.clasterId):
            cluster_path = grains_settings_XML.getGrainSettings(
                'clusterPath/cluster', 'fileRepository')[index]
            file_multiplicator = len(grains_settings_XML.getGrainSettings(
                'clusterPath/cluster/@filesAmount', 'fileRepository')[index])

    file_ver_cursor = fileVersionCursor(context)
    file_ver_cursor.setRange('fileId', file_id)

    try:
        for file_ver in file_ver_cursor.iterate():
            if file_ver.exist:
                current_file = throughListToPath(
                    cluster_path, file_ver.fileName, file_multiplicator)
                os.remove(current_file)
            file_ver.delete()

        file_cursor.delete()
        return True
    except OSError:
        raise Exception(
            u'Файлов, указанных в таблице fileVersion как существующие,\
            не обнаружено.')


def throughListToPath(cluster_path, file_name, file_multiplicator):
    '''
    Функция перегоняет путь к кластеру + имя файла в полноценный путь к файлу.
    Также требуется file_multiplicator - количество десятичных разрядов
    определяемое по количеству файлов, указанное в grainsSettings filesAmpunt.
    '''
    path_to_file = [cluster_path]  # Путь до кластера
    # Путь до файла, последний элемент - порядковый номер файла
    path_to_file.extend(nameToPathList(file_name, file_multiplicator)[:-1])
    # Собственно файл
    path_to_file.append(file_name)
    path_to_file = os.path.abspath('\\'.join(path_to_file))  # Обращаем в путь
    return path_to_file


def downloadFile(context, file_id):
    '''
    Осуществляем загрузку файла, версия которого - последняя,
    ну или добавлен последним.
    '''

    file_cursor = fileCursor(context)
    file_version_cursor = fileVersionCursor(context)

    try:
        file_cursor.get(file_id)
    except:
        context.error(
            u'В функцию, осуществляющую скачивание, передан неверный ID.')

    file_version_cursor.setRange('fileId', file_cursor.id)
    file_version_cursor.setRange('exist', True)
    file_version_cursor.orderBy('fileName')
    file_version_cursor.tryLast()

    if not file_version_cursor:
        context.error(u'Файл не найден.')

    dict_settings = pullGrainSettings(context, file_version_cursor.clasterId)
    file_multiplicator = len(str(dict_settings['filesAmount']))

    path_to_file = throughListToPath(
        dict_settings['clusterPath'], file_version_cursor.fileName,
        file_multiplicator)
    out_stream = FileInputStream(path_to_file)

    return JythonDownloadResult(out_stream, file_cursor.name)


def grainsSettingsPath():
    '''Функция возвращает путь к grainsSettings.xml'''
    path_to_grainsS = os.path.abspath(__file__)
    path_to_grainsS = os.path.join(
        path_to_grainsS[:path_to_grainsS.find('common.sys')],
        'grainsSettings.xml')
    if not os.path.exists(path_to_grainsS):
        return None
    return path_to_grainsS


def profilactic(context):
    '''
    Функция удаляет всё содержимое кластера,
    если папка под него существует (1) и список логов fileVersion пуст.
    '''
    import shutil

    grains_settings_XML = SettingsManager(context)
    file_counter_cursor = fileCounterCursor(context)
    file_version_cursor = fileVersionCursor(context)

    for file_counter in file_counter_cursor.iterate():
        file_version_cursor.setRange('clasterId', file_counter.clasterId)
        if not file_version_cursor.count():
            for index, cur_num in enumerate(
                    grains_settings_XML.getGrainSettings(
                        'clusterPath/cluster/@number', 'fileRepository')):
                if cur_num == str(file_counter.clasterId):
                    clusterPath = grains_settings_XML.getGrainSettings(
                        'clusterPath/cluster', 'fileRepository')[index]
                    break

            if os.path.exists(clusterPath):
                root, dirs, files = os.walk(clusterPath).next()
                '''Чистим директорию от посторонних объектов.'''
                try:
                    for directory in dirs:
                        shutil.rmtree(os.path.join(root, directory))
                    for fil in files:
                        os.remove(os.path.join(root, fil))
                except:
                    context.error(
                        u'Недостаточно прав для очистки \
                        выбранной под кластер папки. Выберите другой адрес.')


def pullGrainSettings(context, cluster=None):
    ''' Возвращает словарь с настройками кластера'''
    grains_settings_XML = SettingsManager(context)
    cluster_numbers = grains_settings_XML.getGrainSettings(
        'clusterPath/cluster/@number', 'fileRepository')

    if cluster:
        for index, cur_num in enumerate(cluster_numbers):
            if cur_num == str(cluster):
                dict_with_values = {
                    'clusterPath': grains_settings_XML.getGrainSettings(
                        'clusterPath/cluster', 'fileRepository')[index],
                    'clusterNumber': int(cur_num),
                    'nestingSize': int(grains_settings_XML.getGrainSettings(
                        'clusterPath/cluster/@nestingSize',
                        'fileRepository')[index]),
                    'filesAmount': int(grains_settings_XML.getGrainSettings(
                        'clusterPath/cluster/@filesAmount',
                        'fileRepository')[index])
                }
                break
    else:
        dict_with_values = {
            'clusterPath': grains_settings_XML.getGrainSettings(
                'clusterPath/cluster', 'fileRepository'),
            'clusterNumber': int_list(cluster_numbers),
            'nestingSize': int_list(grains_settings_XML.getGrainSettings(
                'clusterPath/cluster/@nestingSize', 'fileRepository')),
            'filesAmount': int_list(grains_settings_XML.getGrainSettings(
                'clusterPath/cluster/@filesAmount', 'fileRepository'))
        }

    return dict_with_values


def clusterInit(context):
    '''
    Сверяем кластеры из grainsSettings и те, которые имеются в БД
    '''
    file_counter_cursor = fileCounterCursor(context)
    grains_settings_XML = SettingsManager(context)

    clasters_dict = {
        'clusterPath': grains_settings_XML.getGrainSettings(
            'clusterPath/cluster', 'fileRepository'),
        'clusterNumber': grains_settings_XML.getGrainSettings(
            'clusterPath/cluster/@number', 'fileRepository'),
        'nestingSize': grains_settings_XML.getGrainSettings(
            'clusterPath/cluster/@nestingSize', 'fileRepository'),
        'filesAmount': grains_settings_XML.getGrainSettings(
            'clusterPath/cluster/@filesAmount', 'fileRepository')
    }

    for cluster in int_list(clasters_dict['clusterNumber']):
        if not file_counter_cursor.tryGet(cluster):
            file_counter_cursor.clasterId = cluster
            file_counter_cursor.latestFileName = 0
            file_counter_cursor.insert()


def repairNullString(path_to_file):
    '''
    Из-за размера буфера в малых файлах
    последняя строка может быть заполнена нулевыми символами.
    Эта функция их устраняет.
    '''
    f = open(path_to_file, 'r')
    need = False

    if f.readlines()[-1][0] == chr(0):
        need = True

    if need:
        f.seek(0)
        file_text = ''.join(f.readlines()[:-1])
        f.close()

        f = open(path_to_file, 'w')
        f.write(file_text)

    f.close()


def getCharById(context, file_id, native_filename=False, upload_ver=False,
                claster_id=False, file_names_dict=False,
                last_file_version_id=False):
    '''
    По id без особых хлопот предоставим пользователю данные о файле.
    '''
    if native_filename or upload_ver:
        file_cursor = fileCursor(context)
        file_cursor.get(file_id)

        return file_cursor.name if native_filename else file_cursor.uploadVersioning

    file_version_cursor = fileVersionCursor(context)
    file_version_cursor.setRange('fileId', file_id)

    if claster_id:
        return {file_version.fileName: file_version.clasterId
                for file_version in file_version_cursor.iterate()}

    if file_names_dict:
        return [file_version.fileName
                for file_version in file_version_cursor.iterate()]

    if last_file_version_id:
        return file_version_cursor.tryLast()


def clusterCreator(context, path_to_cluster, cluster_num=None):
    '''
    Не используется.
    Создаём кластер, если номер указан и он не существует,
    либо создаём новый кластер, если предыдущие заполнены. 
    '''
    clusterInit(context)

    if not cluster_num:
        cluster_num, necessity = newClasterCheck(context)
        cluster_num = int(cluster_num) + 1
        if necessity:
            raise Exception(u'Последний использовавшийся кластер не заполнен. \
            Либо откажитесь от намерения создать новый кластер, \
            либо укажите его числовой номер при вызове функции clusterCreator.')
    '''Расшифровка: 0,4,5 и 2 - отступы, 1 - порядковый номер кластера,
    3 - путь к кластеру'''
    cluster_record_template = '''{0}<cluster number="{1}">\n{2}{3}\n{4}</cluster>\n{5}'''
    tab = ' ' * 4
    cluster_record = cluster_record_template.format(
        tab, cluster_num, 5 * tab, path_to_cluster, 4 * tab, 3 * tab)

    path_to_grainsS = grainsSettingsPath()
    if not path_to_grainsS:
        raise Exception(
            u'Прежде чем создавать кластер, \
            надо создать файл с настройками grainsSettings.')

    changeFile(path_to_grainsS, cluster_record,
               'clusterPath', add=True, at_end=True)

    return True


def newClasterCheck(context, claster_num=None):
    '''
    Не используется.
    Проверяем, нужен ли новый кластер и, если нужен,
    то создаём, называется он следующим порядковым номером.
    '''
    file_counter_cursor = fileCounterCursor(context)
    grains_settings_XML = SettingsManager(context)
    cluster_counter = 0

    nesting_size = int(
        grains_settings_XML.getGrainSettings('nestingSize',
                                             'fileRepository')[0])
    files_amount = int(
        grains_settings_XML.getGrainSettings('filesAmount',
                                             'fileRepository')[0])
    file_multiplicator = len(str(files_amount))

    if not claster_num:
        file_counter_cursor.orderBy('clasterId')
        file_counter_cursor.tryLast()
        claster_num = file_counter_cursor.clasterId
    else:
        file_counter_cursor.get(claster_num)

    new_cluster = [claster_num]
    files_and_folders = nameToPathList(
        file_counter_cursor.latestFileName, file_multiplicator)

    for file_or_folder in files_and_folders:
        if file_or_folder >= files_amount:
            cluster_counter += 1

    if cluster_counter >= nesting_size:
        new_cluster.append(True)
    else:
        new_cluster.append(False)
    return new_cluster


def changeFile(path_to_file, added_string, enter_tag, add=None,
               change=None, at_end=None):
    '''
    Не используется (и не будет, скорее всего)
    added_string - строка (готовая!), которая будет добавлена в файл;
    enter - тег, открывающий в который надо вставлять кусок текста;
    add/change - мод (пока работает для частного случая);
    at_end - если надо добавить в самый конец тега текст;
    Функция добавляет кластер или правит кривые настройки кластера
    Потом можно будет допилить
    '''
    added_string = unicode(added_string)  # На всякий пожарный
    try:
        opened_file = open(path_to_file, 'r')
        string_file = opened_file.read()
        opened_file.close()
    except Exception as err:
        raise Exception(err)

    if at_end:
        start_position = escape_position = string_file.find(
            '</%s>' % enter_tag)
    elif change:
        start_position = string_file.find(
            '<%s>' % enter_tag) + len(enter_tag) + 2
        escape_position = string_file.find('</%s>' % enter_tag)

    string_file = '%s%s%s' % (string_file[:start_position],
                              added_string,
                              string_file[escape_position:])

    opened_file = open(path_to_file, 'w')
    opened_file.write(string_file)
    opened_file.close()


def int_list(default_list):
    return [int(element) for element in default_list]
