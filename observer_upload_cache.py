import pathlib


# this makes no appologies for multiple hashes having the same values, I'm not opening that can of worms at present
class ObserverCache:

    # this is a data structure containing a hash of the data of every file on the server, and a list of file paths
    # with that hash, we can query this when data is uploaded so we can duplicate local files as necessary
    # rather than reupload files
    cache_map = {}

    # def remove_path(self, path_in):
    #     remove_list = []
    #     for c_hash in self.hash_map:
    #         # if this path is in the hash map remove it
    #         if path_in in self.hash_map[c_hash]:
    #             remove_list.append(c_hash)
    #     for c_hash in remove_list:
    #         self.hash_map[c_hash].remove(path_in)
    #         # if there are no longer any tied paths remove the hash
    #         if not len(self.hash_map[c_hash]):
    #             self.hash_map.pop(c_hash, None)

    def add_contents(self, path_in: pathlib.Path):
        self.cache_map[path_in] = path_in.read_text()

    # def move_hash(self, origin_in, path_in):
    #     remove_list = []
    #     for c_hash in self.hash_map:
    #         # if this path is in the hash map remove it
    #         if origin_in in self.hash_map[c_hash]:
    #             remove_list.append(c_hash)
    #     for c_hash in remove_list:
    #         self.hash_map[c_hash].remove(origin_in)
    #         self.hash_map[c_hash].append(path_in)
    #
    # def hash_exists(self, path_in):
    #     hash_in = get_hash(path_in)
    #     return path_in in self.hash_map[hash_in]
    #
    # def get_hash_path(self, hash_in):
    #     if hash_in in self.hash_map:
    #         return self.hash_map[hash_in][0]
    #     return None
