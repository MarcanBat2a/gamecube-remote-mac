import sys

if len(sys.argv) > 1 and sys.argv[1] == '--bleak-subprocess':
    sys.argv = [sys.argv[0]] + sys.argv[2:]  # strip flag
    from gc_controller.ble.bleak_subprocess import main as bleak_main
    bleak_main()
else:
    from gc_controller.app import main
    main()
