from app.schemas import EnergyRecommendation, EnergyRequest


class EnergyService:
    def recommend(self, req: EnergyRequest) -> EnergyRecommendation:
        annual = sum(req.monthly_kwh)
        solar_generation = req.solar_capacity_kw * 950
        usable_solar = min(annual, solar_generation * 0.82)
        coverage = 100 * usable_solar / annual if annual else 0
        savings = usable_solar * req.tariff_eur_kwh
        actions = []
        if annual > 4200:
            actions.append("Prioritize insulation and heating-system efficiency assessment")
        if req.solar_capacity_kw == 0:
            actions.append("Evaluate rooftop solar potential")
        elif coverage < 55:
            actions.append("Evaluate additional solar capacity or battery storage")
        actions.append("Shift flexible loads to low-demand or solar-generation hours")
        return EnergyRecommendation(
            annual_kwh=round(annual, 1),
            estimated_cost_eur=round(annual * req.tariff_eur_kwh, 2),
            estimated_solar_coverage_pct=round(coverage, 1),
            annual_savings_eur=round(savings, 2),
            actions=actions,
        )
