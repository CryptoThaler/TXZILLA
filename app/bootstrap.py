from app.services.database_init_service import DatabaseInitService


def main() -> None:
    result = DatabaseInitService().bootstrap()
    print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
