import logging
from cache import Cache
from memory import Memory

class CPU:
    def __init__(self, cache=None, memory=None):
        # Initialize CPU with 32 general purpose registers, following the MIPS conventions
        # R0 is hardwired to 0, R7 is used for return addresses
        logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - CPU: %(message)s'
                )
        self.logger = logging.getLogger(__name__)

        self.memory = memory if memory else Memory()
        self.cache = cache if cache else Cache()
        self.pc = 0
        self.registers = {}
        for i in range(32):
            self.registers[f"R{i}"] = 0

        # R0 should always be 0
        self.registers['R0'] = 0
        self.running = True
        self.logger.info("CPU initialized")
        self.logger.debug(f"Initial register state: {self.registers}")

    def reset(self):
        # reset the CPU to initial state
        self.pc = 0
        for reg in self.registers:
            self.registers[reg] = 0
        self.running = True
        self.logger.info("CPU reset")
        
    def fetch_instruction(self, instruction):
        # parse an instruction
        try:
            parts = instruction.strip().split(',')
            operation = parts[0]
            operands = parts[1:] if len(parts) > 1 else []

            self.logger.debug(f"Fetched instruction: {operation} with operands {operands}")
            return operation, operands
        except Exception as e:
            self.logger.error(f"Error fetching instruction: {str(e)}") 
            raise

    def execute_instruction(self, instruction):
        # execute an instruction
        try:
            operation, operands = self.fetch_instruction(instruction)

            if operation == "ADD":
                self.execute_add(operands)
            elif operation == "ADDI":
                self.execute_addi(operands)
            elif operation == "SUB":
                self.execute_sub(operands)
            elif operation == "SLT":
                self.execute_slt(operands)
            elif operation == "BNE":
                self.execute_bne(operands)
            elif operation == "J":
                self.execute_jump(operands)
            elif operation == "JAL":
                self.execute_jal(operands)
            elif operation == "LW":
                self.execute_lw(operands)
            elif operation == "SW":
                self.execute_sw(operands)
            elif operation == "CACHE":
                self.execute_cache(operands)
            elif operation == "HALT":
                self.running = False
                self.logger.info("CPU Halted")
            else:
                self.logger.error(f"Unknown operation: {operation}")
                raise ValueError(f"Unknown operation: {operation}")

        except Exception as e:
            self.logger.error(f"Error executing instruction: {str(e)}")
            raise

    def execute_add(self, operands):
        # ADD Rd, Rs, Rt
        # Rd = Rs + Rt
        try:
            rd, rs, rt = operands
            rs_value = self.registers[rs]
            rt_value = self.registers[rt]
            result = rs_value + rt_value

            if rd != 'R0':
                self.registers[rd] = result

            self.logger.debug(f"ADD: {rd} = {rs}({rs_value}) + {rt}({rt_value}) = {result}")
            self.pc += 4 # increment program counter

        except Exception as e:
            self.logger.error(f"Error executing ADD: {str(e)}")
            raise

    def execute_addi(self, operands):
        # ADDI Rd, Rs, immd
        # Rd = Rs + immd
        try:
            rt, rs, immd = operands
            rs_value = self.registers[rs]
            immd_value = int(immd)
            result = rs_value + immd_value

            if rt != 'R0':
                self.registers[rt] = result

            self.logger.debug(f"ADDI: {rt} = {rs}({rs_value}) + {immd} = {result}")
            self.pc += 4 # increment program counter

        except Exception as e:
            self.logger.error(f"Error executing ADDI: {str(e)}")
            raise

    def execute_sub(self, operands):
        # SUB Rd, Rs, Rt
        # Rd = Rs - Rt
        try:
            rd, rs, rt = operands
            rs_value = self.registers[rs]
            rt_value = self.registers[rt]
            result = rs_value - rt_value

            if rd != 'R0':
                self.registers[rd] = result

            self.logger.debug(f"SUB: {rd} = {rs}({rs_value}) - {rt}({rt_value}) = {result}")
            self.pc += 4 # increment program counter

        except Exception as e:
            self.logger.error(f"Error executing SUB: {str(e)}")
            raise

    def execute_slt(self, operands):
        # SLT Rd, Rs, Rt
        # If (Rs < Rt) then Rd = 1 else Rd = 0
        try:
            rd, rs, rt = operands
            rs_value = self.registers[rs]
            rt_value = self.registers[rt]

            result = 1 if rs_value < rt_value else 0

            if rd != 'R0':
                self.registers[rd] = result

            self.logger.debug(f"SLT: {rd} = ({rs}({rs_value}) < {rt}({rt_value})) = {result}")
            self.pc += 4 # increment program counter

        except Exception as e:
            self.logger.error(f"Error executing SLT: {str(e)}")
            raise
        
    def execute_bne(self, operands):
        # BNE Rs, Rt, offset
        # If Rs != Rt then branch to PC + 4 + offset
        try:
            rs, rt, offset = operands
            rs_value = self.registers[rs]
            rt_value = self.registers[rt]
            offset_value = int(offset)

            self.pc += 4

            if rs_value != rt_value:
                self.pc += (offset_value * 4) # branch taken
                self.logger.debug(f"BNE: branch taken. New PC = {self.pc}")
            else:
                self.logger.debug(f"BNE: branch not taken. PC = {self.pc}")

        except Exception as e:
            self.logger.error(f"Error executing BNE: {str(e)}")
            raise

    def execute_jump(self, operands):
        # J target
        # Jump to target address
        try:
            target = int(operands[0])
            self.pc = target * 4 # target is an address, so multiply by 4
            self.logger.debug(f"JUMP: New PC = {self.pc}")

        except Exception as e:
            self.logger.error(f"Error executing JUMP: {str(e)}")
            raise

    def execute_jal(self, operands):
        # JAL target
        # Jump to target address and save return address in R7
        try:
            target = int(operands[0])

            self.registers['R7'] = self.pc + 4
            self.pc = target * 4

            self.logger.debug(f"JAL: Return address {self.registers['R7']} stored in R7. New PC = {self.pc}")

        except Exception as e:
            self.logger.error(f"Error executing JAL: {str(e)}")
            raise

    def execute_lw(self, operands):
        # LW Rt, offset(Rs)
        # Load word from memory at address Rs + offset into Rt
        try:
            rt = operands[0]
            offset_rs = operands[1]

            offset_str = offset_rs.split('(')[0]
            rs = offset_rs.split('(')[1].rstrip(')')

            offset_value = int(offset_str)
            rs_value = self.registers[rs]
            address = rs_value + offset_value

            value = self.cache.cache_read(address)

            if rt != 'R0':
                self.registers[rt] = value

            self.logger.debug(f"LW: {rt} = MEM[{rs}({rs_value}) + {offset_value}] = {value}")
            self.pc += 4

        except Exception as e:
            self.logger.error(f"Error executing LW: {str(e)}")
            raise

    def execute_sw(self, operands):
        # SW Rt, offset(Rs)
        # Store word from Rt to memory at address Rs + offset
        try:
            rt = operands[0]
            offset_rs = operands[1]

            offset_str = offset_rs.split('(')[0]
            rs = offset_rs.split('(')[1].rstrip(')')

            offset_value = int(offset_str)
            rs_value = self.registers[rs]
            address = rs_value + offset_value

            rt_value = self.registers[rt]
            self.cache.cache_write(address, rt_value)

            self.logger.debug(f"SW: MEM[{rs}({rs_value}) + {offset_value}] = {rt}({rt_value})")
            self.pc += 4

        except Exception as e:
            self.logger.error(f"Error executing SW: {str(e)}")
            raise

    def execute_cache(self, operands):
        # Cache Code
        # Code = 0: Disable Cache, Code = 1: Enable Cache, Code = 2: Flush Cache
        try:
            code = int(operands[0])
            self.cache.cache_control(code)
            self.logger.debug(f"CACHE: Control code {code} executed")
            self.pc += 4

        except Exception as e:
            self.logger.error(f"Error executing CACHE: {str(e)}")
            raise
