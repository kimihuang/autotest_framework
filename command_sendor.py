from abc import ABC, abstractmethod
import serial
import time

class CommandSender(ABC):
    @abstractmethod
    def send_command(self, command: str) -> None:
        pass
    
    def format_command(self, command: str) -> str:
        # Add any common command formatting logic here
        return f"{command}\n"

class ConsoleCommandSender(CommandSender):
    def send_command(self, command: str) -> None:
        formatted_command = self.format_command(command)
        print(f"[Console Mode] Sending: {formatted_command.strip()}")

class UartCommandSender(CommandSender):
    def __init__(self, port: str, baudrate: int = 115200):
        self.serial = serial.Serial(port=port, 
                                  baudrate=baudrate,
                                  timeout=1)
    
    def send_command(self, command: str) -> None:
        formatted_command = self.format_command(command)
        print(f"[UART Mode] Sending: {formatted_command.strip()}")
        self.serial.write(formatted_command.encode())
        # Add delay if needed between commands
        time.sleep(0.1)
        
        # Read and print response
        response = self.serial.readline().decode().strip()
        if response:
            print(f"Response: {response}")
    
    def __del__(self):
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()
