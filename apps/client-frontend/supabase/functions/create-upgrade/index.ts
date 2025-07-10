
import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import Stripe from "https://esm.sh/stripe@14.21.0";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const logStep = (step: string, details?: any) => {
  const detailsStr = details ? ` - ${JSON.stringify(details)}` : '';
  console.log(`[CREATE-UPGRADE] ${step}${detailsStr}`);
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

    // Get the plan from request body
    const { planId } = await req.json();
    if (!planId || !['pro', 'premium'].includes(planId)) {
      throw new Error("Invalid plan ID provided");
    }
    logStep("Plan ID received", { planId });

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

    // Define plan prices
    const planPrices = {
      pro: 3900, // R$ 39.00
      premium: 9900 // R$ 99.00
    };

    // Create new price if it doesn't exist
    const newPriceAmount = planPrices[planId as keyof typeof planPrices];
    const planNames = {
      pro: "Plano Pro",
      premium: "Plano Premium"
    };

    // Create a new price for the target plan
    const newPrice = await stripe.prices.create({
      currency: "brl",
      unit_amount: newPriceAmount,
      recurring: { interval: "month" },
      product_data: {
        name: planNames[planId as keyof typeof planNames]
      }
    });

    logStep("Created new price", { priceId: newPrice.id, amount: newPriceAmount });

    // Update the subscription to the new plan with proration
    const updatedSubscription = await stripe.subscriptions.update(
      currentSubscription.id,
      {
        items: [{
          id: currentSubscription.items.data[0].id,
          price: newPrice.id,
        }],
        proration_behavior: 'create_prorations',
        metadata: {
          user_id: user.id,
          plan: planId,
          upgrade_date: new Date().toISOString()
        }
      }
    );

    logStep("Subscription updated with proration", { 
      subscriptionId: updatedSubscription.id,
      newPlan: planId,
      newPrice: newPriceAmount 
    });

    // Get the upcoming invoice to show the user what they'll be charged
    const upcomingInvoice = await stripe.invoices.retrieveUpcoming({
      customer: customerId,
      subscription: updatedSubscription.id,
    });

    const prorationAmount = upcomingInvoice.amount_due;
    logStep("Calculated proration amount", { prorationAmount });

    return new Response(JSON.stringify({ 
      success: true,
      subscriptionId: updatedSubscription.id,
      prorationAmount: prorationAmount,
      newPlan: planId,
      message: prorationAmount > 0 
        ? `Upgrade realizado! Você será cobrado R$${(prorationAmount / 100).toFixed(2)} proporcional ao período restante.`
        : prorationAmount < 0
        ? `Downgrade realizado! Você receberá um crédito de R$${Math.abs(prorationAmount / 100).toFixed(2)} na próxima fatura.`
        : "Plano atualizado com sucesso!"
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logStep("ERROR in create-upgrade", { message: errorMessage });
    return new Response(JSON.stringify({ error: errorMessage }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 500,
    });
  }
});
