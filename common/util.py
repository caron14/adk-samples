from dotenv import load_dotenv, find_dotenv


def load_env() -> None:
    """
    Load environment variables from .env file.
    
    Searches for .env file in parent directories and loads
    environment variables from it.
    """
    _ = load_dotenv(find_dotenv())


if __name__ == "__main__":
    pass
