def main():
    parser = argparse.ArgumentParser(description='Automated Test Framework')
    parser.add_argument('--mode', choices=['console', 'uart'], default='console',
                      help='Execution mode: console or uart')
    parser.add_argument('--port', default='/dev/ttyUSB0',
                      help='UART port (only needed in uart mode)')
    parser.add_argument('--config', default='test_config.yml',
                      help='Path to test configuration file')
    parser.add_argument('--case', help='Specific test case to run (optional)')
    
    args = parser.parse_args()
    
    # Create appropriate command sender based on mode
    if args.mode == 'uart':
        sender = UartCommandSender(port=args.port)
    else:
        sender = ConsoleCommandSender()
    
    # Initialize framework
    config = TestConfig(args.config)
    framework = TestFramework(sender, config)
    
    # Run tests
    if args.case:
        framework.run_test_case(args.case)
    else:
        framework.run_all_test_cases()

if __name__ == "__main__":
    main()
