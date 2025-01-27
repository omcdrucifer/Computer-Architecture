from collections import deque
import logging
from memory import Memory

class Cache:
    def __init__(self, main_memory=None, cache_size=16):
        logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - Cache: %(message)s'
                )
        self.logger = logging.getLogger(__name__)

        self.main_memory = main_memory if main_memory else Memory()
        self.cache_size = cache_size
        self.cache = deque(maxlen=cache_size)
        self.enabled = False
        self.dirty_entries = set()

        self.hits = 0
        self.misses = 0
        self.total_access_time = 0
        self.total_accesses = 0

        self.logger.info(f"Cache initialized with size {cache_size}")

    def sync_with_memory(self):
        try:
            for entry in self.cache:
                if entry['address'] in self.dirty_entries:
                    self.main_memory.write_word(entry['address'], entry['data'])
            self.dirty_entries.clear()
            self.logger.info("Cache synced with main memory")
        except Exception as e:
            self.logger.error(f"Error during memory sync: {str(e)}")
            raise

    def cache_read(self, address):
        if not self.enabled:
            return self.main_memory.read_word(address)

        self.total_accesses += 1

        for entry in self.cache:
            if entry['address'] == address:
                self.hits += 1
                self.total_access_time += 1

                self.logger.debug(f"Cache hit: read {entry['data']} from {address}")
                return entry['data']

        self.misses += 1

        self.total_access_time += 10
        data = self.main_memory.read_word(address)
        self.update_cache(address, data)
        self.logger.debug(f"Cache miss: loaded {data} from {address}")
        return data

    def get_cache_status(self):
        try:
            current_size = len(self.cache)
            dirty_count = len(self.dirty_entries)
            capacity = self.cache_size
            utilization = (current_size / capacity) * 100 if capacity > 0 else 0

            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            avg_access_time = (self.total_access_time / total_requests) if total_requests > 0 else 0

            status = {
                    'enabled': self.enabled,
                    'current_size': current_size,
                    'capacity': capacity,
                    'utilization': utilization,
                    'dirty_entries': dirty_count,
                    'cached_addresses': [entry['address'] for entry in self.cache],
                    'hits': self.hits,
                    'misses': self.misses,
                    'hit_rate': f"{hit_rate:.2f}%",
                    'average_access_time': f"{avg_access_time:.2f} units"
                    }

            self.logger.info(f"Cache Status: {status}")
            return status

        except Exception as e:
            self.logger.error(f"Error getting cache status: {str(e)}")
            raise

    def cache_write(self, address, data):
        if not self.enabled:
            self.main_memory.write_word(address, data)
            return

        self.update_cache(address, data)
        self.dirty_entries.add(address)
        self.logger.debug(f"Cache write: stored {data} to {address}")

    def update_cache(self, address, data):
        self.cache = deque(entry for entry in self.cache if entry['address'] != address)

        self.cache.append({'address': address, 'data': data})

    def cache_control(self, code):
        if code == 0:
            self.enabled = False
            self.logger.info("Cache disabled")
        elif code == 1:
            self.enabled = True
            self.logger.info("Cache enabled")
        elif code == 2:
            self.flush()
        else:
            self.logger.error(f"Invalid cache control code: {code}")
            raise ValueError(f"Invalid cache control code: {code}")

    def flush(self):
        self.sync_with_memory()
        self.cache.clear()
        self.logger.info("Cache flushed")
