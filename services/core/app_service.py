from services.core.portfolio_service import PortfolioService
from services.core.market_service import MarketService
from services.core.trading_service import TradingService

class AppService:
    def __init__(self):
        self.portfolio_service = PortfolioService()
        self.market_service = MarketService()
        self.trading_service = TradingService(
            self.portfolio_service,
            self.market_service
        )
    
    def get_portfolio_service(self) -> PortfolioService:
        return self.portfolio_service
    
    def get_trading_service(self) -> TradingService:
        return self.trading_service
    
    def get_market_service(self) -> MarketService:
        return self.market_service