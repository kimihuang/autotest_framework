import time
from typing import Dict, Any

from command_sender import CommandSender
from config import TestConfig

class TestFramework:
    def __init__(self, sender: CommandSender, config: TestConfig):
        self.sender = sender
        self.config = config
        
    def run_test_case(self, case_name: str) -> None:
        commands = self.config.get_commands()
        if case_name not in commands:
            raise ValueError(f"Test case '{case_name}' not found in config")
            
        case_commands = commands[case_name]
        print(f"\nExecuting test case: {case_name}")
        
        for cmd_info in case_commands:
            if isinstance(cmd_info, dict):
                cmd = cmd_info.get('command', '')
                delay = cmd_info.get('delay', 0)
            else:
                cmd = cmd_info
                delay = 0
                
            self.sender.send_command(cmd)
            if delay > 0:
                time.sleep(delay)
    
    def run_all_test_cases(self) -> None:
        commands = self.config.get_commands()
        for case_name in commands:
            self.run_test_case(case_name)
