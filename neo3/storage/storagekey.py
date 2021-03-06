import mmh3  # type: ignore
from neo3.core import serialization, types, Size as s, utils


class StorageKey(serialization.ISerializable):
    def __init__(self, contract: types.UInt160 = None, key: bytes = None):
        self.contract = contract if contract else types.UInt160.zero()
        self.key = key if key else b''

    def __len__(self):
        # TODO: see if there is a cleaner way of doing this
        with serialization.BinaryWriter() as bw:
            bw.write_bytes_with_grouping(self.key)
            key_len = len(bw._stream.getvalue())
        return s.uint160 + key_len

    def __eq__(self, other):
        if type(other) is type(self):
            return self.contract == other.contract and self.key == other.key
        else:
            return False

    def __hash__(self):
        return hash(self.contract) + mmh3.hash(self.key, seed=0, signed=False)

    def __repr__(self):
        return f"<{self.__class__.__name__} at {hex(id(self))}> [{self.contract}] {self.key}"

    def serialize(self, writer: serialization.BinaryWriter) -> None:
        writer.write_serializable(self.contract)
        writer.write_bytes_with_grouping(self.key, group_size=16)

    def deserialize(self, reader: serialization.BinaryReader) -> None:
        self.contract = reader.read_serializable(types.UInt160)
        self.key = reader.read_bytes_with_grouping(group_size=16)

    @staticmethod
    def create_grouped_prefix(key_prefix: bytes, group_size) -> bytes:
        if group_size >= 255:
            raise ValueError("group_size must be < 254")

        output = b''
        index = 0
        remainder = len(key_prefix)
        while remainder >= group_size:
            output += key_prefix[index:index + group_size]
            output += bytes([group_size])
            index += group_size
            remainder -= group_size

        if remainder > 0:
            output += key_prefix[index:]
        return output
