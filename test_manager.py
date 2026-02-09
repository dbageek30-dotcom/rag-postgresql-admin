from agency.decision.manager import DBAManager


def main():
    mgr = DBAManager()

    print("\n=== Test Manager : pgBackRest info ===")
    result = mgr.handle("/tool info")
    print(result)

    print("\n=== Test Manager : SQL ===")
    result = mgr.handle("/sql SELECT version();")
    print(result)

    print("\n=== Test Manager : Documentation ===")
    result = mgr.handle("/doc explain pgbackrest stanza")
    print(result)


if __name__ == "__main__":
    main()

