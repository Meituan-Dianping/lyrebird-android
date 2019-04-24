import lyrebird
import pip


if __name__ == '__main__':
    version_num = pip.__version__[:pip.__version__.find('.')]
    if int(version_num) >= 10:
        from pip import __main__
        __main__._main(['install', '.',  '--upgrade'])
    else:
        pip.main(['install', '.',  '--upgrade'])
    lyrebird.main()

