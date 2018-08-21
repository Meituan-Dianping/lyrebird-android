import lyrebird
import pip


if __name__ == '__main__':
    pip.main(['install', '.',  '--upgrade'])
    lyrebird.debug()
