import logging
from cpu import CPU
from cache import Cache
from memory import Memory

def read_instructions(filename):
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        logging.error(f"Could not find instruction file: {filename}")
        raise
    except Exception as e:
        logging.error(f"Error reading instructions: {str(e)}")
        raise

def main():
    logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - Main: %(message)s'
            )
    logger = logging.getLogger(__name__)

    try:
        memory = Memory("data_input.txt")
        cache = Cache(main_memory=memory)
        cpu = CPU(memory=memory, cache=cache)

        instructions = read_instructions("instruction_input.txt")
        logger.info(f"Loaded {len(instructions)} instructions")

        instruction_count = 0
        while cpu.running and instruction_count < len(instructions):
            current_instruction = instructions[instruction_count]
            cpu.execute_instruction(current_instruction)
            instruction_count += 1

        logger.info(f"Program completed. Executed {instruction_count} instructions")

        cache_stats = cache.get_cache_status()
        logger.info(f"Final cache statistics: {cache_stats}")

    except Exception as e:
        logger.error(f"Program execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
