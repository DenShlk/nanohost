import sys
import uuid


class DummyStorage:
    data: dict[int, str] = {}
    size: int

    def store(self, content) -> int:
        uid = uuid.uuid4().int
        while uid in self.data:
            uid = uuid.uuid4().int
        self.data[uid] = content
        return uid

    def get(self, uid: int) -> str:
        return self.data[uid]

    def count(self) -> int:
        return len(self.data)

    def size(self) -> int:
        return sys.getsizeof(self.data)


