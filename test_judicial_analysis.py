"""
Test script for the judicial auction analysis functionality
"""

from judicial_analysis import JudicialAuctionAnalyzer
import json
from datetime import datetime

# Sample test text that contains various elements we need to analyze
test_text = """
EDITAL DE LEILÃO JUDICIAL

O Dr. João Carlos Silva, MM. Juiz de Direito da 3ª Vara Cível da Comarca de São Paulo/SP,
FAZ SABER a todos quanto o presente edital virem ou dele conhecimento tiverem e interessar
possa que, nos autos do processo nº 1234567-89.2024.8.26.0100, de Execução Fiscal movida
pela PREFEITURA MUNICIPAL DE SÃO PAULO em face de EMPRESA EXEMPLO LTDA, CNPJ 12.345.678/0001-90,
foi designada a venda do bem abaixo descrito.

DATAS DOS LEILÕES:
1ª Praça: 15/03/2024 às 14:00 horas - Valor mínimo: R$ 850.000,00
2ª Praça: 25/03/2024 às 14:00 horas - Valor mínimo: R$ 425.000,00 (50% da avaliação)

PUBLICAÇÃO DO EDITAL: O presente edital foi publicado no Diário Oficial do Estado em 08/03/2024
e no jornal Folha de São Paulo em 09/03/2024, respeitando o prazo legal de antecedência mínima
de 5 (cinco) dias úteis.

INTIMAÇÕES: Ficam devidamente INTIMADOS através deste edital, caso não sejam localizados para
intimação pessoal, o executado EMPRESA EXEMPLO LTDA, na pessoa de seu representante legal,
bem como sua sócia MARIA DA SILVA, CPF 987.654.321-00, o cônjuge do executado, se casado for,
e o credor hipotecário BANCO EXEMPLO S.A., CNPJ 98.765.432/0001-10, nos termos do artigo 889,
incisos I, II e V do CPC.

DESCRIÇÃO DO IMÓVEL:
Apartamento nº 101, localizado no 10º andar do Edifício Exemplo, situado na Rua das Flores,
nº 123, Bairro Jardim Exemplo, São Paulo/SP, CEP 01234-567, com área privativa de 120m²,
matrícula nº 123.456 do 5º Cartório de Registro de Imóveis de São Paulo/SP.

AVALIAÇÃO: R$ 850.000,00 (oitocentos e cinquenta mil reais) em janeiro de 2024.

ÔNUS: Consta da matrícula:
- R.5: Hipoteca em favor do BANCO EXEMPLO S.A. no valor de R$ 300.000,00
- AV.6: Penhora referente aos presentes autos

DÉBITOS:
- IPTU: R$ 15.345,67 (exercícios 2022 a 2024)
- Condomínio: R$ 8.234,50 (últimos 6 meses)
- Total de débitos: R$ 23.580,17

Os débitos de IPTU e condomínio serão sub-rogados no valor da arrematação, nos termos do
art. 130, parágrafo único do CTN e art. 908, §1º do CPC.

SITUAÇÃO DO IMÓVEL: O imóvel encontra-se DESOCUPADO, livre de pessoas e coisas, conforme
auto de constatação juntado aos autos, facilitando a imissão na posse pelo arrematante.

CONDIÇÕES DA ARREMATAÇÃO: O arrematante arcará com os custos da arrematação, incluindo
a comissão do leiloeiro de 5% sobre o valor da arrematação.

O presente edital será afixado e publicado na forma da lei.

São Paulo, 08 de março de 2024.

Dr. João Carlos Silva
Juiz de Direito
"""

def test_judicial_analyzer():
    """Test the judicial auction analyzer with sample text"""
    print("=== Testing Judicial Auction Analyzer ===\n")
    
    # Initialize analyzer
    analyzer = JudicialAuctionAnalyzer()
    
    # Pre-extracted entities for testing (simulating what would come from text_worker)
    test_entities = {
        "cnpj": ["12.345.678/0001-90", "98.765.432/0001-10"],
        "cpf": ["987.654.321-00"],
        "process_number": ["1234567-89.2024.8.26.0100"],
        "money": ["R$ 850.000,00", "R$ 425.000,00", "R$ 300.000,00", "R$ 15.345,67", "R$ 8.234,50"],
        "date": ["15/03/2024", "25/03/2024", "08/03/2024", "09/03/2024"],
        "cep": ["01234-567"],
        "area": ["120m²"]
    }
    
    # Analyze the text
    print("Analyzing document...")
    result = analyzer.analyze(text=test_text, entities=test_entities)
    
    # Convert to dict for display
    result_dict = result.dict()
    
    # Print summary of findings
    print("\n=== ANALYSIS RESULTS ===\n")
    
    print(f"1.1 AUCTION TYPE: {result.auction_type.value}")
    print(f"    Confidence: {result.auction_type_confidence:.1%}")
    print(f"    Indicators: {', '.join(result.auction_type_indicators[:3])}...")
    
    print(f"\n1.2 PUBLICATION COMPLIANCE:")
    print(f"    Diário Oficial: {'✓' if result.publication_compliance.diario_oficial_mentioned else '✗'}")
    print(f"    Newspaper: {'✓' if result.publication_compliance.newspaper_mentioned else '✗'}")
    print(f"    Days between publication and auction: {result.publication_compliance.days_between_publication_auction or 'N/A'}")
    print(f"    Meets deadline: {'✓' if result.publication_compliance.meets_deadline_requirement else '✗'}")
    print(f"    Compliance: {result.publication_compliance.compliance_status.value}")
    
    print(f"\n1.3-1.4 CPC 889 NOTIFICATIONS:")
    print(f"    Executado notified: {'✓' if result.executado_notification and result.executado_notification.notification_mentioned else '✗'}")
    print(f"    Other parties notified: {len(result.other_notifications)}")
    print(f"    CPC 889 Compliance: {result.cpc_889_compliance.value}")
    
    print(f"\n1.5 VALUATION ANALYSIS:")
    print(f"    Market value: R$ {result.valuation.market_value:,.2f}" if result.valuation.market_value else "    Market value: Not found")
    print(f"    1st auction: R$ {result.valuation.first_auction_value:,.2f}" if result.valuation.first_auction_value else "    1st auction: Not found")
    print(f"    2nd auction: R$ {result.valuation.second_auction_value:,.2f}" if result.valuation.second_auction_value else "    2nd auction: Not found")
    print(f"    2nd auction percentage: {result.valuation.second_auction_percentage:.1f}%" if result.valuation.second_auction_percentage else "    2nd auction percentage: N/A")
    print(f"    Below 50%: {'⚠️ YES - RISK' if result.valuation.below_50_percent else '✓ NO'}")
    
    print(f"\n1.6 DEBTS:")
    print(f"    IPTU: R$ {result.debts.iptu_debt:,.2f}" if result.debts.iptu_debt else "    IPTU: Not found")
    print(f"    Condominium: R$ {result.debts.condominium_debt:,.2f}" if result.debts.condominium_debt else "    Condominium: Not found")
    print(f"    Total debt: R$ {result.debts.total_debt:,.2f}" if result.debts.total_debt else "    Total debt: Not calculated")
    print(f"    Responsibility: {result.debts.debt_responsibility}")
    
    print(f"\n1.7 PROPERTY STATUS:")
    print(f"    Occupancy: {result.property_status.occupancy_status.value}")
    print(f"    Details: {result.property_status.occupancy_details}")
    print(f"    Possession transfer risk: {result.property_status.possession_transfer_risk}")
    
    print(f"\n1.8 LEGAL RESTRICTIONS:")
    print(f"    Has restrictions: {'YES' if result.legal_restrictions.restrictions_found else 'NO'}")
    print(f"    Restrictions: {', '.join(result.legal_restrictions.restrictions_found) if result.legal_restrictions.restrictions_found else 'None'}")
    print(f"    Transfer viability: {result.legal_restrictions.transfer_viability}")
    
    print(f"\n=== FINAL ASSESSMENT ===")
    print(f"Overall Risk Score: {result.overall_risk_score:.0f}/100")
    print(f"Investment Viability: {result.investment_viability_score:.0f}/100")
    print(f"Analysis Confidence: {result.confidence_level:.1%}")
    
    print(f"\nCOMPLIANCE ISSUES ({len(result.compliance_issues)}):")
    for issue in result.compliance_issues:
        print(f"  - {issue}")
    
    print(f"\nRECOMMENDATIONS ({len(result.recommendations)}):")
    for rec in result.recommendations:
        print(f"  - {rec}")
    
    # Save full results to file
    output_file = "test_judicial_analysis_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\n✓ Full results saved to: {output_file}")
    
    return result

if __name__ == "__main__":
    test_judicial_analyzer()