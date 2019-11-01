from DirectoryLoader import DirectoryLoader

if __name__ == '__main__':
    loader = DirectoryLoader('/home/nowork/test_web')
    files = loader.get_file_dict()
    print(files)
