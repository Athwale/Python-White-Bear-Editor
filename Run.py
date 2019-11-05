from DirectoryLoader import DirectoryLoader

if __name__ == '__main__':
    loader = DirectoryLoader('/home/gill/test_web')
    files = loader.get_file_dict()
    print(files)
