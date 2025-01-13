from abc import ABC, abstractmethod
import serial
import time
import sys
import select
import threading
import queue

class CommandResponse:
    def __init__(self, command: str, response: str, success: bool = True, error: str = None):
        self.command = command
        self.response = response
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.success = success
        self.error = error

    def __str__(self):
        status = "SUCCESS" if self.success else "FAILED"
        result = f"[{self.timestamp}] {status}\nCommand: {self.command}\nResponse: {self.response}"
        if self.error:
            result += f"\nError: {self.error}"
        return result

class CommandSender(ABC):
    def __init__(self):
        self.response_queue = queue.Queue()
        
    @abstractmethod
    def send_command(self, command: str) -> CommandResponse:
        pass
    
    def format_command(self, command: str) -> str:
        return f"{command}\n"

class ConsoleCommandSender(CommandSender):
    def __init__(self):
        super().__init__()
        self._start_console_reader()

    def _start_console_reader(self):
        self.console_thread = threading.Thread(target=self._console_reader, daemon=True)
        self.console_thread.start()

    def _console_reader(self):
        while True:
            # 检查是否有控制台输入
            if select.select([sys.stdin], [], [], 0.1)[0]:
                response = sys.stdin.readline().strip()
                self.response_queue.put(response)

    def send_command(self, command: str) -> CommandResponse:
        formatted_command = self.format_command(command)
        print(f"\n[Console Mode] Sending: {formatted_command.strip()}")
        print("Enter response (press Enter for success, or type custom response):")
        
        try:
            # 等待响应，设置超时时间为30秒
            response = self.response_queue.get(timeout=30)
            success = not response.startswith("ERROR:")
            error = response[6:] if response.startswith("ERROR:") else None
            return CommandResponse(command, response, success, error)
        except queue.Empty:
            return CommandResponse(command, "", False, "Response timeout")

class UartCommandSender(CommandSender):
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0):
        super().__init__()
        self.serial = serial.Serial(port=port, baudrate=baudrate, timeout=timeout)
        self.read_thread = threading.Thread(target=self._read_serial, daemon=True)
        self.read_thread.start()
        
    def _read_serial(self):
        while self.serial.is_open:
            if self.serial.in_waiting:
                try:
                    line = self.serial.readline().decode().strip()
                    if line:
                        self.response_queue.put(line)
                except Exception as e:
                    print(f"Serial reading error: {e}")
            time.sleep(0.1)
    
    def send_command(self, command: str) -> CommandResponse:
        if not self.serial.is_open:
            return CommandResponse(command, "", False, "Serial port not open")
            
        formatted_command = self.format_command(command)
        print(f"\n[UART Mode] Sending: {formatted_command.strip()}")
        
        try:
            # 清空之前的响应
            while not self.response_queue.empty():
                self.response_queue.get_nowait()
                
            # 发送命令
            self.serial.write(formatted_command.encode())
            
            # 收集响应（等待直到收到特定结束标记或超时）
            responses = []
            timeout = time.time() + 5  # 5秒超时
            
            while time.time() < timeout:
                try:
                    response = self.response_queue.get(timeout=0.5)
                    responses.append(response)
                    
                    # 检查是否是结束标记（可以根据实际协议修改）
                    if response.strip() in ["OK", "ERROR"] or "Done" in response:
                        break
                except queue.Empty:
                    continue
            
            combined_response = "\n".join(responses)
            success = "ERROR" not in combined_response
            error = None if success else combined_response
            
            return CommandResponse(command, combined_response, success, error)
            
        except Exception as e:
            return CommandResponse(command, "", False, str(e))
    
    def __del__(self):
        if hasattr(self, 'serial') and self.serial.is_open:
            self.serial.close()