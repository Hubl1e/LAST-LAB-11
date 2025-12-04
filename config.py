from configparser import ConfigParser

def load_config(filename='database.ini', section='postgresql'): #загружаем конфги
    parser = ConfigParser()
    parser.read(filename)

    config = {} #создается пустой словарь чтобы туда вписывать то што ниже
    if parser.has_section(section):
        params = parser.items(section)
        for param in params: #проверяем каждый ключ и значение и добавляем параметр в конфиг
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename)) #если секции нет то ошбика

    return config

if __name__ == '__main__': #блок выполнится токо если напряммую запускать
    config = load_config() #вызывается функция конфига
    print(config)

