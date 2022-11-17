from typing import *
import os

class listFilepathsFromDirectory:

    def __init__(self) -> None:
        pass

    def query(self, dirpath: str, extension: str = "", limit: int = 0) -> list:
        """Query file paths from given directory path.

        Parameters
        ----------
        dirpath : str
            Directory path, eg. "C:\\temp"
        extension : str, optional
            Filter by file extensions (eg. ".json"), by default ""
        limit : int, optional
            Limit number of results, by default 0

        Returns
        -------
        list
            Filepaths
        """

        assert os.path.isdir(dirpath)
        filepaths = []
        fileCount = 0

        for file in os.listdir(dirpath):
            if limit and fileCount == limit:
                continue

            filepath = os.path.join(dirpath, file)
            
            if os.path.isfile(filepath):
                if extension and os.path.splitext(filepath)[1] == extension:
                    filepaths.append(filepath)
                    fileCount += 1
                elif not extension:
                    filepaths.append(filepath)
                    fileCount += 1

        return filepaths

def main():

    filepaths = listFilepathsFromDirectory().query(
                                                  dirpath = r"C:\temp\UnrealPakTool", 
                                                  extension = ".json", 
                                                  limit = 5
                                                )

    print(filepaths)

    return

if __name__ == "__main__":
    main()
