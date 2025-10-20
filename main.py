# main.py
from rich.console import Console
from app.cli.menu_printer import MenuPrinter
from app.service.login_service import LoginService
from app.service.user_service import UserService
from app.service.portfolio_service import PortfolioService
from app.service.security_service import SecurityService
from db import seed_initial_data

console = Console()

def main() -> None:
    # seed already called in db import, but safe to call again if needed
    seed_initial_data()
    login_service = LoginService()
    menu = MenuPrinter(login_service, UserService(), PortfolioService(), SecurityService())
    menu.run()

if __name__ == "__main__":
    main()
