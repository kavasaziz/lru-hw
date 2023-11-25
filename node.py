import time

class Node:
    def __init__(self, key, value, expiration, priority):
        self.key = key
        self.value = value
        self.expiration = expiration
        self.priority = priority
        self.prev = None
        self.next = None


class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}  # Maps key to node
        self.head = Node(None, None, None, None)  # Dummy head
        self.tail = Node(None, None, None, None)  # Dummy tail
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove_node(self, node):
        prev, nxt = node.prev, node.next
        prev.next, nxt.prev = nxt, prev

    def _add_node_to_front(self, node):
        node.next = self.head.next
        node.next.prev = node
        self.head.next = node
        node.prev = self.head

    def _move_to_front(self, node):
        self._remove_node(node)
        self._add_node_to_front(node)

    def _evict(self):
        # Evict expired items first
        current = self.tail.prev
        while current != self.head and current.expiration < time.time():
            self.cache.pop(current.key)
            self._remove_node(current)
            current = self.tail.prev

        # If still over capacity, evict based on priority and recency
        if len(self.cache) > self.capacity:
            current = self.tail.prev
            lowest_priority = current.priority
            while current != self.head and current.priority == lowest_priority:
                current = current.prev
            current = current.next  # Move to the first node with lowest priority
            self.cache.pop(current.key)
            self._remove_node(current)

    def insert(self, key, value, expiration, priority):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            node.expiration = expiration
            node.priority = priority
            self._move_to_front(node)
        else:
            if len(self.cache) >= self.capacity:
                self._evict()
            new_node = Node(key, value, expiration, priority)
            self.cache[key] = new_node
            self._add_node_to_front(new_node)

    def delete(self, key):
        if key in self.cache:
            node = self.cache.pop(key)
            self._remove_node(node)

    def update(self, key, value, expiration, priority):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            node.expiration = expiration
            node.priority = priority
            self._move_to_front(node)

    def get(self, key):
        if key in self.cache:
            node = self.cache[key]
            if node.expiration < time.time():  # Check for expiration
                self.delete(key)
                return None
            self._move_to_front(node)
            return node.value
        return None

# Example usage
cache = LRUCache(3)
cache.insert("a", 1, time.time() + 5, 2)  # key "a", value 1, expires in 5 seconds, priority 2
cache.insert("b", 2, time.time() + 10, 1)  # key "b", value 2, expires in 10 seconds, priority 1
cache.insert("c", 3, time.time() + 15, 3)  # key "c", value 3, expires in 15 seconds, priority 3
print(cache.get("a"))  # Should return 1
time.sleep(6)  # Wait for "a" to expire
print(cache.get("a"))  # Should return None as "a" is expired
cache.insert("d", 4, time.time() + 20, 2)  # Insert "d", causing eviction if needed
print(cache.get("b"))  # Should return 2
print(cache.get("c"))  # Should return 3
print(cache.get("d"))  # Should return 4
