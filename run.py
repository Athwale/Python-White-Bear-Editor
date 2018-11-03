from DirectoryLoader import DirectoryLoader

if __name__ == '__main__':
    loader = DirectoryLoader("/home/omejzlik/Pers/web/testWeb")
    files = loader.get_file_dict()
    for file in files:
        print(files[file])
