
import { PlanDetails } from '@/types';
import { Check } from 'lucide-react';

interface PlanComparisonProps {
  planDetails: PlanDetails[];
}

export function PlanComparison({ planDetails }: PlanComparisonProps) {
  return (
    <div className="mt-12 border rounded-lg overflow-hidden">
      <div className="bg-muted p-4">
        <h3 className="text-lg font-medium">Comparativo de planos</h3>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-muted/50">
              <th className="px-4 py-3 text-left font-medium">Funcionalidade</th>
              {planDetails.map((plan) => (
                <th key={plan.id} className="px-4 py-3 text-center font-medium">
                  {plan.name}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {planDetails[0].features.map((feature, idx) => (
              <tr key={idx} className="border-t">
                <td className="px-4 py-3 text-sm">{feature.title}</td>
                
                {planDetails.map((plan) => {
                  const isFeatureEnabled = plan.features[idx][plan.id];
                  
                  return (
                    <td key={plan.id} className="px-4 py-3 text-center">
                      {isFeatureEnabled ? (
                        <Check className="h-4 w-4 mx-auto text-accent" />
                      ) : (
                        <div className="h-4 w-4 mx-auto" />
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
