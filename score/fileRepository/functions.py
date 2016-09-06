# coding: UTF-8
'''
Created 28.02.2016 by s.gavrilov
'''
from array import array
from datetime import datetime
from java.io import FileOutputStream, BufferedInputStream
import os

from common.grainssettings import SettingsManager
from common.numbersseries.getNextNo import getNextNoOfSeries
from fileRepository._fileRepository_orm import fileCounterCursor, \
    fileCursor, fileVersionCursor


def putFile(context, native_filename, stream_input, current_cluster_num=1,
            rewritten_file_id=None, uploadVersioning=False):
    """Функция, записывающая файл в кластер и пишет данные о нём в БД
       данные о кластере берутся из grainSettings

       native_filename - имя загружаемого файла,
       stream_input - входящий java поток,
       current_cluster_num - номер кластера, в который следует положить файл,
       rewritten_file_id - если передаётся id файла, то его переписываем,
       uploadVersioning - если True, сохраняем предыдущую версию файла,
                          иначе - удаляем.
    """

    file_version_cursor = fileVersionCursor(context)
    file_cursor = fileCursor(context)
    file_count_cursor = fileCounterCursor(context)

    """Проверка на существование кластера"""
    if not file_count_cursor.tryGet(int(current_cluster_num)):
        context.error(u"В таблице кластеров переданный id не содержится.")

    """Имена для серий номеров."""
    file_NS_name = "filesNS"
    file_vers_NS_name = "fileVerNS"

    """Путь к создающемуся файлу, имя файла на сервере,
    словарь с данными из generalSettings"""
    path_to, digit_file_name, amount_and_nest = getPathToFile(
        context, current_cluster_num)

    file_multiplicator = len(str(amount_and_nest["filesAmount"]))

    if not rewritten_file_id:
        """Если файл новый"""
        file_cursor.id = getNextNoOfSeries(context, file_NS_name)
        file_cursor.name = native_filename
        file_cursor.uploadVersioning = uploadVersioning
    else:
        """Записываем новую версию существующего файла:
            Если uploadVersioning = False, то старая версия файла удаляется,
        """
        if not file_cursor.tryGet(rewritten_file_id):
            context.error(
                u"Перезаписываемый файл не найден.")
        file_cursor.name = native_filename
        file_version_cursor.setRange("fileId", rewritten_file_id)
        file_version_cursor.setRange("exist", True)
        """Если не поддерживается сохранение предыдущей версии"""
        if not file_cursor.uploadVersioning:
            """Ищем предыдущую версию файла."""
            if file_version_cursor.tryFirst():
                path_to_old_file = getFilePathByParams(
                    amount_and_nest['clusterPath'],
                    file_version_cursor.fileName,
                    file_multiplicator)  # Получаем путь из имени файла
                """и удаляем"""
                try:
                    os.remove(path_to_old_file)
                except OSError:
                    context.error(u"Ошибочный путь к файлу внутри системы.")
            """Предыдущая версия удаляется => не существует"""
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

    """Обновление/Добавление кластера в таблице fileCounter."""
    refresher = 1
    for file_counter in file_count_cursor.iterate():
        if file_counter.clasterId == amount_and_nest["clusterNumber"]:
            file_counter.latestFileName = digit_file_name
            file_counter.update()
            refresher = 0

    if refresher:
        file_count_cursor.clasterId = amount_and_nest["clusterNumber"]
        file_count_cursor.latestFileName = digit_file_name
        file_count_cursor.insert()

    """Собственно, запись файла."""
    fileToWrite = FileOutputStream(path_to)
    size_of_file = 0
    stream_size = 4096
    buffer_stream = BufferedInputStream(stream_input, stream_size)
    d = array("b", [0] * stream_size)

    try:
        c = buffer_stream.read(d, 0, stream_size)
        while c != -1:
            fileToWrite.write(d[:c])
            size_of_file += 1
            c = buffer_stream.read(d, 0, stream_size)
    finally:
        stream_input.close()
        fileToWrite.close()

    if 0 < size_of_file < 8:
        repairNullString(path_to)
    """3апись в БД в случае, если при загрузке не произошла ошибка"""
    if not rewritten_file_id:
        file_cursor.insert()
    else:
        file_cursor.update()
    file_version_cursor.insert()

    return {
        "file_version_id": file_version_cursor.id,
        "file_id": file_cursor.id
    }


def getPathToFile(context, current_cluster_num):
    """Функция, которая дополняет иерархию внутри кластера
       до заданной в grainssettings, и возвращает имя текущего файла"""

    """Получаем словарь с настройками данного кластера"""
    cluster_settings = getClusterSettings(context, current_cluster_num)
    """Проверяем, существует ли данный кластер. Если нет, то создаём."""
    try:
        if not os.path.exists(cluster_settings["clusterPath"]):
            os.makedirs(cluster_settings["clusterPath"])
    except OSError:
        context.error(u"Указывайте адрес кластера в существующей директории.")

    # Получаем количество разрядов под общее число файлов(папок) в папке
    name_length = len(str(cluster_settings["filesAmount"]))
    temp_path = cluster_settings["clusterPath"]

    files_version_cursor = fileVersionCursor(context)
    files_version_cursor.orderBy("fileName")
    files_version_cursor.tryLast()

    """Проверка, была ли информация в grainsSettings изменена."""
    if files_version_cursor.fileName:
        aspect_ratio = len(files_version_cursor.fileName) // name_length
        if aspect_ratio != cluster_settings["nestingSize"] + 1:
            context.error(u"Данные в grainsSettings были изменены \
            в процессе эксплуатации БД. \
            Чтобы дальнейшая работа была корректной, \
            следует очистить таблицы fileVersion и file.")

    if files_version_cursor.fileName:
        """ Следующая функция создаёт следующий по порядку файл и
        прописывает(создает) для него путь """
        path_to_file = createDirectories(
            temp_path, files_version_cursor.fileName,
            name_length, cluster_settings["filesAmount"])
        file_name = os.path.basename(path_to_file)   # Вытаскиваем имя файла
        if not path_to_file:
            context.error(
                u"В текущих кластерах слишком много файлов,\
                создайте новый кластер.")
    else:
        import shutil
        root, dirs, files = os.walk(temp_path).next()
        """Чистим директорию от посторонних объектов."""
        try:
            for directory in dirs:
                shutil.rmtree(os.path.join(root, directory))
            for fil in files:
                os.remove(os.path.join(root, fil))
        except:
            context.error(
                u"Недостаточно прав для очистки выбранной под кластер папки. \
                Выберите другой адрес.")
        """Создаём путь до первого файла в кластере."""
        i = 0
        while i < cluster_settings["nestingSize"]:
            # Составляем путь до папки, где будут лежать файлы
            temp_path += "\\%s" % "1".zfill(name_length)
            os.mkdir(os.path.abspath(temp_path))
            i += 1

        # Составляем имя первого файла в кластере
        file_name = "1".zfill(name_length) * \
            (cluster_settings["nestingSize"] + 1)
        path_to_file = os.path.join(temp_path, file_name)

    return path_to_file, file_name, cluster_settings


def createDirectories(path, file_name, name_length, restriction):
    """Функция возвращает полный путь до ещё не созданного файла, либо None,
       если внутри кластера нет места
       path - путь к текущему кластеру,
       file_name - имя последнего добавленного файла,
       name_length - длина названия файла/директории,
                     определяется числом разрядов filesAmount,
       restriction - максимально допустимое количество объектов в каждой папке"""

    dir_names = nameToPathList(file_name, name_length)

    dir_names = toIntList(dir_names)
    dir_names[-1] += 1  # Создаём имя для следующего файла
    flex_dir_names = []
    jump = 0
    """Цикл проверяет новосозданный путь к файлу на превышения,
    указанные в restriction (grainssettings)."""
    for index, dir_name in enumerate(dir_names[::-1]):
        current_name = dir_name + jump  # Текущее "имя" файла/директории
        if current_name > restriction:
            """При выполнении кластер заполнен."""
            if index == name_length:
                return None
            """Создание имени новой директории или файла, без разницы."""
            flex_dir_names.append(1)
            jump = 1
        else:
            flex_dir_names.append(current_name)
            jump = 0

    dir_names = flex_dir_names[::-1]
    file_name = ""
    """Создаём корректный путь к размещаемому файлу."""
    dir_names = [str(x).zfill(name_length) for x in dir_names]
    for dir_name in dir_names[:-1]:
        path = os.path.join(path, dir_name)
        if not os.path.isdir(path):
            os.mkdir(path)
    """Составляем имя файла."""
    file_name = "".join(dir_names)
    return os.path.join(path, file_name)


def nameToPathList(file_name, name_length):
    """Функция, возвращающая списком путь к файлу
       из его названия (относительно кластера)
       """
    dir_names = []
    for i in xrange(name_length):
        dir_names.append(
            file_name[i * name_length: (i + 1) * name_length]
        )

    return dir_names


def deleteFile(context, file_id):
    """Удаление файла из кластера и данных о нём из БД"""
    file_cursor = fileCursor(context)
    file_ver_cursor = fileVersionCursor(context)

    if not file_cursor.tryGet(file_id):
        context.error(u"Файл не найден")

    file_ver_cursor.setRange("fileId", file_id)

    try:
        for file_ver in file_ver_cursor.iterate():
            if file_ver.exist:
                current_file = getFilePathById(context, file_id, file_ver.id)
                os.remove(current_file)
        file_ver.deleteAll()

        file_cursor.delete()
        return True
    except OSError:
        raise Exception(
            u"Файлы, указанные в таблице fileVersion как существующие,\
            не найдены.")


def getFilePathByParams(cluster_path, file_name, name_length):
    """Функция возвращает путь к файлу
       cluster_path - путь к кластеру
       file_name - название файла
       name_length - длина названия файла/директории,
                     определяется числом разрядов filesAmount,
    """
    path_to_file = [cluster_path]  # Путь до кластера
    # Путь до файла, последний элемент - порядковый номер файла
    path_to_file.extend(nameToPathList(file_name, name_length)[:-1])
    # Собственно файл
    path_to_file.append(file_name)
    path_to_file = os.path.abspath("\\".join(path_to_file))  # Обращаем в путь
    return path_to_file


def getFilePathById(context, file_id, file_version_id=None):
    "Функция возвращает путь к последней версии файла либо к указанной"
    file_cursor = fileCursor(context)
    file_version_cursor = fileVersionCursor(context)

    if not file_cursor.tryGet(file_id):
        context.error(u"Файл не найден.")

    if not file_version_id:
        file_version_cursor.setRange("fileId", file_cursor.id)
        file_version_cursor.setRange("exist", True)
        file_version_cursor.orderBy("fileName desc")
    else:
        file_version_cursor.setRange("id", file_version_id)

    if not file_version_cursor.tryFirst():
        context.error(u"Файл не найден.")

    dict_settings = getClusterSettings(context, file_version_cursor.clasterId)
    nestingSize = len(str(dict_settings["filesAmount"]))
    return getFilePathByParams(
        dict_settings["clusterPath"],
        file_version_cursor.fileName,
        nestingSize)


def getRelativePathById(context, file_id, file_version_id=None):
    "Функция возвращает относительный путь к последней версии файла либо к указанной"
    file_cursor = fileCursor(context)
    file_version_cursor = fileVersionCursor(context)

    if not file_cursor.tryGet(file_id):
        return

    if not file_version_id:
        file_version_cursor.setRange("fileId", file_cursor.id)
        file_version_cursor.setRange("exist", True)
        file_version_cursor.orderBy("fileName desc")
    else:
        file_version_cursor.setRange("id", file_version_id)

    if not file_version_cursor.tryFirst():
        return
    dict_settings = getClusterSettings(context, file_version_cursor.clasterId)
    nestingSize = len(str(dict_settings["filesAmount"]))
    path_to_file = []
    path_to_file.extend(nameToPathList(file_version_cursor.fileName,
                                       nestingSize)[:-1])
    # Собственно файл
    path_to_file.append(file_version_cursor.fileName)
    return path_to_file


def profilactic(context):
    """Функция очищает кластеры от неуказанных в базе файлов,
        если все файлы в кластере являются неуказанными"""
    import shutil

    grains_settings_XML = SettingsManager(context)
    file_counter_cursor = fileCounterCursor(context)
    file_version_cursor = fileVersionCursor(context)

    for file_counter in file_counter_cursor.iterate():
        file_version_cursor.setRange("clasterId", file_counter.clasterId)
        if not file_version_cursor.count():
            for index, cur_num in enumerate(
                    grains_settings_XML.getGrainSettings(
                        "clusterPath/cluster/@number", "fileRepository")):
                if cur_num == str(file_counter.clasterId):
                    clusterPath = grains_settings_XML.getGrainSettings(
                        "clusterPath/cluster", "fileRepository")[index]
                    break

            if os.path.exists(clusterPath):
                root, dirs, files = os.walk(clusterPath).next()
                """Чистим директорию от посторонних объектов."""
                try:
                    for directory in dirs:
                        shutil.rmtree(os.path.join(root, directory))
                    for fil in files:
                        os.remove(os.path.join(root, fil))
                except:
                    context.error(
                        u"Недостаточно прав для очистки \
                        выбранной под кластер папки. Выберите другой адрес.")


def getClusterSettings(context, cluster=None):
    """ Возвращает словарь с настройками всех кластеров или конкретного,
        если передан его номер"""
    grains_settings_XML = SettingsManager(context)
    cluster_numbers = grains_settings_XML.getGrainSettings(
        "clusterPath/cluster/@number", "fileRepository")

    if cluster:
        for index, cur_num in enumerate(cluster_numbers):
            if cur_num == str(cluster):
                dict_with_values = {
                    "clusterPath": grains_settings_XML.getGrainSettings(
                        "clusterPath/cluster", "fileRepository")[index],
                    "clusterNumber": int(cur_num),
                    "nestingSize": int(grains_settings_XML.getGrainSettings(
                        "clusterPath/cluster/@nestingSize",
                        "fileRepository")[index]),
                    "filesAmount": int(grains_settings_XML.getGrainSettings(
                        "clusterPath/cluster/@filesAmount",
                        "fileRepository")[index])
                }
                break
    else:
        dict_with_values = {
            "clusterPath": grains_settings_XML.getGrainSettings(
                "clusterPath/cluster", "fileRepository"),
            "clusterNumber": toIntList(cluster_numbers),
            "nestingSize": toIntList(grains_settings_XML.getGrainSettings(
                "clusterPath/cluster/@nestingSize", "fileRepository")),
            "filesAmount": toIntList(grains_settings_XML.getGrainSettings(
                "clusterPath/cluster/@filesAmount", "fileRepository"))
        }

    return dict_with_values


def clusterInit(context):
    """Сравниваем кластеры из grainsSettings и кластеры, указанные в БД,
       если кластер из grainsSettings отсутствует в БД, создаём эту запись"""
    file_counter_cursor = fileCounterCursor(context)
    grains_settings_XML = SettingsManager(context)

    clasters_dict = {
        "clusterPath": grains_settings_XML.getGrainSettings(
            "clusterPath/cluster", "fileRepository"),
        "clusterNumber": grains_settings_XML.getGrainSettings(
            "clusterPath/cluster/@number", "fileRepository"),
        "nestingSize": grains_settings_XML.getGrainSettings(
            "clusterPath/cluster/@nestingSize", "fileRepository"),
        "filesAmount": grains_settings_XML.getGrainSettings(
            "clusterPath/cluster/@filesAmount", "fileRepository")
    }

    for cluster in toIntList(clasters_dict["clusterNumber"]):
        if not file_counter_cursor.tryGet(cluster):
            file_counter_cursor.clasterId = cluster
            file_counter_cursor.latestFileName = 0
            file_counter_cursor.insert()


def repairNullString(path_to_file):
    """Из-за размера буфера в малых файлах
       последняя строка может быть заполнена нулевыми символами.
       Эта функция их устраняет.
    """
    f = open(path_to_file, "r")

    if f.readlines()[-1][0] == chr(0):
        f.seek(0)
        file_text = "".join(f.readlines()[:-1])
        f.close()

        f = open(path_to_file, "w")
        f.write(file_text)

    f.close()


def toIntList(list_of_strings):
    """Функция, интующая переданный в нее список"""
    return map(lambda x: int(x), list_of_strings)
