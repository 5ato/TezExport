from sqlalchemy.orm import Session


class Service:
    def __init__(self, session: Session) -> None:
        self.session: Session = session
        