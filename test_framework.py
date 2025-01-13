
import time
from command_sender import CommandSender
from config import TestConfig


class TestFramework:
    def __init__(self, sender: CommandSender, config: TestConfig):
        self.sender = sender
        self.config = config
        self.test_results = []
        
    def run_test_case(self, case_name: str) -> None:
        commands = self.config.get_commands()
        if case_name not in commands:
            raise ValueError(f"Test case '{case_name}' not found in config")
            
        case_commands = commands[case_name]
        print(f"\nExecuting test case: {case_name}")
        
        case_results = []
        for cmd_info in case_commands:
            if isinstance(cmd_info, dict):
                cmd = cmd_info.get('command', '')
                delay = cmd_info.get('delay', 0)
            else:
                cmd = cmd_info
                delay = 0
                
            response = self.sender.send_command(cmd)
            case_results.append(response)
            print(response)
            
            if delay > 0:
                time.sleep(delay)
        
        self.test_results.append((case_name, case_results))
    
    def run_all_test_cases(self) -> None:
        commands = self.config.get_commands()
        for case_name in commands:
            self.run_test_case(case_name)
    
    def generate_report(self):
        print("\n=== Test Execution Report ===")
        for case_name, results in self.test_results:
            print(f"\nTest Case: {case_name}")
            success_count = sum(1 for r in results if r.success)
            print(f"Success Rate: {success_count}/{len(results)} "
                  f"({success_count/len(results)*100:.1f}%)")
            
            for result in results:
                print(f"\n{result}")