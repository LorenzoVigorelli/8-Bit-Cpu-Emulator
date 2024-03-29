## FUNCTIONS ##

def binary_to_decimal(binary_string):
    # Check if the number is negative
    if binary_string[0] == '1':  
        # Calculate the two's complement by subtracting 2^n
        return int(binary_string, 2) - 2**len(binary_string)
    else:
        return int(binary_string, 2)


def decimal_to_binary(decimal_number, bit_width=8):
    if decimal_number < 0:
        # Calculate the two's complement by adding 2^n
        binary_string = bin(decimal_number + 2**bit_width)[2:]
    else:
        binary_string = bin(decimal_number)[2:]

    # Ensure the binary string has the correct length (bit_width)
    return binary_string.zfill(bit_width)


def hex_to_binary(hex_number, bit_width):
    # remove the 0x if present
    hex_number = hex_number.lstrip("0x")

    # Convert the number in binary and add zeros if necessary
    binary_number = bin(int(hex_number, 16))[2:].zfill(bit_width)[:bit_width]

    return binary_number


## CLASSES ##

# General purpose register
class Register:
    def __init__(self):
        self.state = ''
    
    # Return the state of the register
    def read(self):
        return self.state
    
    # Overwrite the state of the register
    def write(self, data):
        self.state = data
    
    def __str__(self):
        return f"State: {self.state}"


# 8-bit register
class ByteRegister(Register):
    def __init__(self):
        self.state = '0'*8

    def __str__(self):
        return f"State: {self.state}"


# 4-bit register
class NibbleRegister(Register):
    def __init__(self):
        self.state = '0'*4
    
    def __str__(self):
        return f"State: {self.state}"


# RAM: store both the program and the data: 16 adresses of 8 bits each
class RAM(Register):
    def __init__(self):
        # List of 8-bits registers
        self.state = [ByteRegister() for _ in range(16)]

    # Write on the address of the RAM
    def write(self, data, address):
        
        # Data validation
        assert type(data) is str, 'data type error'
        assert len(data) == 8, 'size error'

        self.state[address].write(data)
    
    # Read the address of the RAM
    def read(self, address):
        return self.state[address].read()
    
    def __str__(self):
        return "\n".join([f"Address {i}: {register}" for i, register in enumerate(self.state)])


# IR: you can access the first and the second nibble
class InstructionRegister(ByteRegister):

    def readOpCode(self):
        # Get the first nibble (op-code)
        return self.read()[:4]
    
    def readOperand(self):
        # Get the second nibble (operand)
        return self.read()[4:]

    def __str__(self):
        return f"OpCode: {self.readOpCode()}\nOperand: {self.readOperand()}"


# 4-bits Program counter
class ProgramCounter(NibbleRegister):

    # Update the counter
    def advance(self):       
        # Get the decimal value
        value = int(self.state, 2)
        # Update the counter mod 2**4
        value = (value + 1)%2**4
        # Convert the new value into a 4-bits string
        string = bin(value)[2:].zfill(4)

        self.state = string

    def __str__(self):
        return f"Value: {int(self.state, 2)}"

    
# Generic Flag
class Flag(Register):

    def __init__(self, reg):
        self.state = 0
        self.reg=reg
    
    def update(self):
        self.state=self.state
    
    def __str__(self):
        return f"State: {self.state}"


# Flag minus: sign of the accumulator
class FlagMinus(Flag):

    def update(self):
        if(binary_to_decimal(self.reg.read())<0):
            self.state=1
        else:
            self.state=0

    def read(self):
        self.update(self)
        return self.state


# Flag Carry: carry of the operation
class FlagCarry(Flag): 

    def update(self):
        if binary_to_decimal(self.reg.a.read())+binary_to_decimal(self.reg.b.read()) > pow(2,7)-1:
            self.state=1
        else:
            self.state=0

    def read(self):
        return self.state


# Flag Zero: check if the accumulator is zero
class FlagZero(Flag): 

    def update(self):
        if(binary_to_decimal(self.reg.read())==0):
            self.state=1
        else:
            self.state=0
    def read(self):
        self.update()
        return self.state


# ALU: 8-bit temporary register
class ALU(ByteRegister):

    def __init__(self, aRegister, bRegister):
        self.a = aRegister
        self.b = bRegister
        self.state='0'*8

    # Possible operation: add, sub
    def update(self, mode='add'):
        value_a, value_b=binary_to_decimal(self.a.read()), binary_to_decimal(self.b.read())
        
        if(mode=='add'):
            result=value_a+value_b
        
        elif(mode=='sub'):
            result=value_a-value_b
        self.state=decimal_to_binary(result)[0:8] 

    def read(self, mode='add'):
        # Update the state before the reading operation
        self.update(mode)
        return self.state
        
    def __str__(self):
        self.read()
        return self.state


# Clock and log file
class Clock:
    def __init__(self, cpu, log_file_path="log.txt"):
        self.state = 0
        self.on = True
        self.log_file_path = log_file_path

    def advance(self, cpu):
        # Save the state in the log file
        if self.state == 0:
            # Create the file at first
            with open(self.log_file_path, "w") as log_file:
                log_file.write(f"{cpu}\n")
        else: 
            # Update the file
            with open(self.log_file_path, "a") as log_file:
                log_file.write(f"{cpu}\n")
            
        # Make the clock click
        self.state += 1

    def __str__(self):
        return str(self.state)
    

# RingCounter: periodic counter to control the execution of microinstructions
class RingCounter():
	def __init__(self, n_time_states):
		self.state=0
		self.n_time_states=n_time_states

	def advance(self):
		self.state=(self.state+1)%self.n_time_states
	
	def read(self):
		return self.state
		
	def __str__(self):
		return str(self.state)
     

