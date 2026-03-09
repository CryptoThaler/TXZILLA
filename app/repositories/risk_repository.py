from app.repositories.seed_data import RISK_RECORDS


class RiskRepository:
    def list_risk_layers(self, property_id: str) -> list[dict]:
        return [
            record
            for record in RISK_RECORDS
            if record["property_id"] == property_id
        ]
