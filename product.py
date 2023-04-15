from dataclasses import dataclass

class Product:
    def __init__(self) -> None:
        self.context = None
        self.meta_info = None

@dataclass
class MetaInfo:
    country_code: str = None