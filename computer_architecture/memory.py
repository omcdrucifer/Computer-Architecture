# class object representation of computer memory
import logging

class Memory:
    def __init__(self, data_file="data_input.txt", size=1024):

        logging.basicConfig(
                level=logging.INFO,
                format='%asctime)s - %(levelname)s - Memory: %(message)s'
                )
        self.logger = logging.getLogger(__name__)

        self.size = size
        self.memory = {}
        self.initial_state = {}
        self.initialize_memory(data_file)
        self.logger.info(f"Memory initialized with {size} bytes")

    def initialize_memory(self, filename):
        try:
            with open(filename, 'r') as file:
                for line in file:
                    address, value = line.strip().split(',')
                    address_int = self.check_bounds(address)
                    value_int = int(value)
                    self.check_value(value_int)
                    self.memory[address_int] = value_int
                    self.initial_state[address_int] = value_int
            self.logger.info(f"Memory initialized from file: {filename}")
        except FileNotFoundError:
            self.logger.error(f"Could not find initialization file: {filename}")
            raise
        except Exception as e:
            self.logger.error(f"Error during memory initialization: {str(e)}")
            raise

    def check_bounds(self, address):
        address_int = int(address, 2) if isinstance(address, str) else address
        if address_int >= self.size:
            self.logger.error(f"Memory access error: Address {address} exceeds memory size {self.size}")
            raise MemoryError(f"Address {address} exceeds memory size {self.size}")
        return address_int

    def check_value(self, value):
        if not isinstance(value, int):
            self.logger.error(f"Type error: Memory value must be an integer")
            raise TypeError("Memory values must be integers")
        if value > 0x7FFFFFFF or value < ~0x80000000:
            self.logger.error(f"Overflow error: Value {value} exceeds 32-bit bounds")
            raise OverflowError("Value exceeds 32-bit bounds")

    def read_word(self, address):
        address_int = self.check_bounds(address)
        value = self.memory.get(address_int, 0)
        self.logger.debug(f"Read value {value} from address {address}")
        return value

    def write_word(self, address, value):
        address_int = self.check_bounds(address)
        self.check_value(value)
        self.memory[address_int] = value
        self.logger.debug(f"Wrote value {value} to address {address}")

    def flush(self):
        self.memory.clear()
        self.logger.info("Memory flushed")

    def reset_to_initial(self):
        self.memory = self.initial_state.copy()
        self.logger.info("Memory reset to initial state")


