
import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import Stripe from "https://esm.sh/stripe@14.21.0";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const logStep = (step: string, details?: any) => {
  const detailsStr = details ? ` - ${JSON.stringify(details)}` : '';
  console.log(`[CALCULATE-PRORATION] ${step}${detailsStr}`);
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    logStep("Function started");

    const stripeKey = Deno.env.get("STRIPE_SECRET_KEY");
    if (!stripeKey) throw new Error("STRIPE_SECRET_KEY is not set");
    logStep("Stripe key verified");

    // Create Supabase client using the anon key for user authentication
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? ""
    );

    const authHeader = req.headers.get("Authorization");
    if (!authHeader) throw new Error("No authorization header provided");
    logStep("Authorization header found");

    const token = authHeader.replace("Bearer ", "");
    const { data: userData, error: userError } = await supabaseClient.auth.getUser(token);
    if (userError) throw new Error(`Authentication error: ${userError.message}`);
    const user = userData.user;
    if (!user?.email) throw new Error("User not authenticated or email not available");
    logStep("User authenticated", { userId: user.id, email: user.email });

    // Get the target plan from request body
    const { targetPlan } = await req.json();
    if (!targetPlan || !['pro', 'premium'].includes(targetPlan)) {
      throw new Error("Invalid target plan provided");
    }
    logStep("Target plan received", { targetPlan });

    const stripe = new Stripe(stripeKey, { apiVersion: "2023-10-16" });

    // Get customer from Stripe
    const customers = await stripe.customers.list({ email: user.email, limit: 1 });
    if (customers.data.length === 0) {
      throw new Error("No Stripe customer found. Please create a subscription first.");
    }
    const customerId = customers.data[0].id;
    logStep("Found Stripe customer", { customerId });

    // Get current active subscription
    const subscriptions = await stripe.subscriptions.list({
      customer: customerId,
      status: "active",
      limit: 1,
    });

    if (subscriptions.data.length === 0) {
      throw new Error("No active subscription found. Please create a subscription first.");
    }

    const currentSubscription = subscriptions.data[0];
    logStep("Found active subscription", { subscriptionId: currentSubscription.id });

    // Define plan prices (in centavos)
    const planPrices = {
      pro: 3900, // R$ 39.00
      premium: 9900 // R$ 99.00
    };

    // Get current plan price from the subscription
    const currentPrice = currentSubscription.items.data[0].price.unit_amount || 0;
    const targetPrice = planPrices[targetPlan as keyof typeof planPrices];
    
    logStep("Price comparison", { currentPrice, targetPrice });

    // Calculate the difference between plans
    const priceDifference = targetPrice - currentPrice;
    
    // Get the remaining time in the current billing period
    const now = Math.floor(Date.now() / 1000);
    const periodEnd = currentSubscription.current_period_end;
    const periodStart = currentSubscription.current_period_start;
    const totalPeriodDuration = periodEnd - periodStart;
    const remainingTime = periodEnd - now;
    
    // Calculate prorated amount
    const prorationMultiplier = remainingTime / totalPeriodDuration;
    const prorationAmount = Math.round(priceDifference * prorationMultiplier);
    
    logStep("Proration calculation", { 
      priceDifference, 
      prorationMultiplier, 
      prorationAmount,
      remainingTime,
      totalPeriodDuration
    });

    return new Response(JSON.stringify({ 
      prorationAmount: prorationAmount,
      targetPlan: targetPlan,
      currentSubscription: currentSubscription.id,
      priceDifference: priceDifference,
      prorationMultiplier: prorationMultiplier
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logStep("ERROR in calculate-proration", { message: errorMessage });
    return new Response(JSON.stringify({ error: errorMessage }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 500,
    });
  }
});
