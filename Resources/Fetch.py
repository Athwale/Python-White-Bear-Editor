import os
import sys
from pathlib import Path

from Constants.Constants import Strings


class Fetch:
    """
    Helper class for getting resources like images from the Resources folder.
    """

    @staticmethod
    def get_resource_path(name: str) -> str:
        """
        Return a string path of a resource from the Resources folder.
        :param name: Name of the resource to get.
        :return: Path to the resource on disk.
        :raise FileNotFoundError: if resource is not found
        """
        path = Path(os.path.dirname(sys.argv[0]))
        resource_dir = path.joinpath('Resources')
        resource_path = os.path.join(resource_dir, name)
        if os.path.exists(resource_path):
            return resource_path
        else:
            raise FileNotFoundError(Strings.exception_resource_not_found)
