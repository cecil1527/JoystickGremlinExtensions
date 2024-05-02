import os
from typing import List


class File:
    def __init__(self, abs_root: str, rel_path: str):
        self.abs_root = abs_root
        self.rel_path = rel_path
        
        # read the contents of the file into a list of lines
        self.lines = []
        with open(self.get_abs_path(), "r") as f:
            self.lines = [line for line in f]

    def get_abs_path(self) -> str:
        return os.path.join(self.abs_root, self.rel_path)

    def rename(self, old: str, new: str):
        '''searches name of file, replacing old with new'''
        
        if old == new:
            return

        if old in self.rel_path:
                new_path = self.rel_path.replace(old, new)
                print('  Renaming:')
                print(f'    old: "{self.rel_path}"')
                print(f'    new: "{new_path}"')
                self.rel_path = new_path

    def replace_str(self, old: str, new: str):
        '''searches contents of file, replacing old with new'''

        if old == new:
            return

        for i, line in enumerate(self.lines):
            if old in line:
                # indices are 0-based, but line numbers will be 1-based
                line_num = i + 1
                print('  Replacing:')
                print(f'    {self.get_abs_path()}:{line_num}')
                print(f'    "{old}" with "{new}"')
                self.lines[i] = line.replace(old, new)

    def write(self, root_output_path = None):
        '''writes contents of file to root output path'''
        
        if root_output_path:
            root = root_output_path
        else:
            root = self.abs_root + " - fixed"

        file_path = os.path.join(root, self.rel_path)

        print(f'Writing: "{file_path}"')
        
        # make sure folder exists
        output_dir, _ = os.path.split(file_path)
        os.makedirs(output_dir, exist_ok=True)
        
        with open(file_path, 'w') as f:
            f.writelines(self.lines)


class Uuid:
    def __init__(self, name: str, uuid: str):
        self.__name = name
        self.__uuid = uuid

        # validate
        self.__name = self.__name.strip()
        self.__uuid = self.__uuid.strip()

        # strip some possible copy/paste errors from UUID
        strings = ["{", "}", ".diff", ".lua"]
        for s in strings:
            self.__uuid = self.__uuid.replace(s, "")
        # store in uppercase
        self.__uuid = self.__uuid.upper()
        
        print(f"  name: {self.__name}")
        print(f"  uuid: {self.__uuid}")
        print()

    # getters in case they change how names/uuids are stored (because DCS stores
    # them a little wonky for some reason, idk.)

    def get_jg_name(self) -> str:
        return self.__name

    def get_jg_uuid(self) -> str:
        return self.__uuid

    def get_dcs_name(self) -> str:
        return self.__name

    def get_dcs_uuid(self) -> str:
        # DCS stores UUID middle part in lower case for some reason. 
        # 1. it doesn't matter for the `.diff.lua` file names
        # 2. but it matters for fixing using a joystick button as a shift
        #    modifier, since DCS records the device UUID inside of the
        #    modifiers.lua file
        s = self.__uuid.split('-')
        s[2] = s[2].lower()
        s = "-".join(s)

        return s


class UuidPair:
    '''simple class to keep old and new UUIDs paired up'''
    def __init__(self, old: Uuid, new: Uuid):
        self.old = old
        self.new = new


def make_files(root_dir: str) -> List[File]:
    '''makes Files from files in root'''

    abs_root = os.path.abspath(root_dir)

    files = []
    # https://docs.python.org/3/library/os.html#os.walk
    for _root, _dirs, _files in os.walk(abs_root):
        for file_name in _files:
            abs_file_path = os.path.join(_root, file_name)
            
            # get path relative to our root (not os.walk()'s root!)
            rel_file_path = abs_file_path.replace(abs_root, "")
            rel_file_path = rel_file_path.removeprefix(os.path.sep)

            files.append(File(abs_root, rel_file_path))

    return files


def fix_dcs_files(input_dir: str, uuids: List[UuidPair]):

    # for DCS files, we need to:
    # 1. rename the file
    # 2. replace UUIDs inside of the file

    print("\nFixing DCS Files")
    files = make_files(input_dir)
    for f in files:
        for pair in uuids:
            f.rename(pair.old.get_dcs_name(), pair.new.get_dcs_name())
            f.rename(pair.old.get_dcs_uuid(), pair.new.get_dcs_uuid())
            
            f.replace_str(pair.old.get_dcs_name(), pair.new.get_dcs_name())
            f.replace_str(pair.old.get_dcs_uuid(), pair.new.get_dcs_uuid())
    
    for f in files:
        f.write()


def fix_joystick_gremlin_files(input_dir: str, uuids: List[UuidPair]):

    # for joystick gremlin files, we just need to replace UUIDs inside of the file

    print("\nFixing Joystick Gremlin Files")
    files = make_files(input_dir)
    for f in files:
        for pair in uuids:
            f.replace_str(pair.old.get_jg_name(), pair.new.get_jg_name())
            f.replace_str(pair.old.get_jg_uuid(), pair.new.get_jg_uuid())
    
    for f in files:
        f.write()


if __name__ == "__main__":
    print("Making UUIDs")
    uuids = [
        UuidPair(
            Uuid("R-VPC Stick MT-50", "D16DF230-2812-11ee-8003-444553540000"),
            Uuid("RIGHT VPC Stick MT-50", "557F56C0-FDE9-11EE-8005-444553540000")),
        
        UuidPair(
            Uuid("L-VPC Throttle MT-50CM2", "D81F5B00-2812-11ee-8005-444553540000"),
            Uuid("LEFT VPC Throttle MT-50CM2", "2F0AFA80-FDE9-11EE-8003-444553540000")),
    ]

    fix_dcs_files("Input", uuids)
    fix_joystick_gremlin_files("jg-Profiles", uuids)
    fix_joystick_gremlin_files("jg-Plugins", uuids)

# this script will run through the folders you tell it to and fix DCS files or
# JG files. it's basically just a fancy find and replace.
#
# it's recommended to copy/paste your folders somewhere else (into the directory
# of this script will be easiest), and run the script on those copies just in
# case something gets messed up!

# NOTE you may need to run DCS once and edit a control to get it to save a new
# diff.lua to see what the controller is now called, because the name can change
# too :(

# TODO
# 1. add ability to delete old DCS .diff.lua files no longer used
# 2. instead of calling rename and replace twice (once for name and once for
#    ID), i could join the "name {UUID}"" and try replacing it all at once