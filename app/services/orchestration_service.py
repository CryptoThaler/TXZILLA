from app.agents.investment_agent import InvestmentAgent
from app.agents.land_transition_agent import LandTransitionAgent
from app.agents.market_intelligence_agent import MarketIntelligenceAgent
from app.agents.report_agent import ReportAgent
from app.agents.risk_agent import RiskAgent
from app.agents.search_agent import SearchAgent
from app.agents.valuation_agent import ValuationAgent
from app.schemas.analysis_schema import PropertyAnalysisReport


class StandardOrchestrator:
    def __init__(self) -> None:
        self.search_agent = SearchAgent()
        self.valuation_agent = ValuationAgent()
        self.risk_agent = RiskAgent()
        self.investment_agent = InvestmentAgent()
        self.market_agent = MarketIntelligenceAgent()
        self.land_transition_agent = LandTransitionAgent()
        self.report_agent = ReportAgent()

    def run(self, property_id: str) -> PropertyAnalysisReport:
        property_detail = self.search_agent.get_property(property_id)
        market_context = self.market_agent.evaluate(property_detail)
        valuation = self.valuation_agent.evaluate(property_detail, market_context)
        risk = self.risk_agent.evaluate(property_detail)
        investment = self.investment_agent.evaluate(
            property_detail,
            market_context,
            valuation,
            risk,
        )
        land_transition = self.land_transition_agent.evaluate(property_detail)
        return self.report_agent.compile(
            property_detail,
            market_context,
            valuation,
            risk,
            investment,
            land_transition,
        )
