from dataclasses import dataclass, field

from dotenv import load_dotenv
from os import getenv


load_dotenv()


@dataclass
class DatabaseConfig:
    DBNAME: str = field(default=getenv('DBNAME'))
    DBPASSWORD: str = field(default=getenv('DBPASSWORD'))
    DBUSER: str = field(default=getenv('DBUSER'))
    DBPORT: str = field(default=getenv('DBPORT'))
    DBSERVER: str = field(default=getenv('DBSERVER'))


@dataclass
class BotConfig:
    TOKEN: str = field(default=getenv('TOKEN'))


BotSettings = BotConfig()
DatabaseSettings = DatabaseConfig()
