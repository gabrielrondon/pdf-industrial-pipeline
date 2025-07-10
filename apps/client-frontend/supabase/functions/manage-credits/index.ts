
import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const logStep = (step: string, details?: any) => {
  const detailsStr = details ? ` - ${JSON.stringify(details)}` : '';
  console.log(`[MANAGE-CREDITS] ${step}${detailsStr}`);
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    logStep("Function started");

    // Create Supabase client using the service role key for admin operations
    const supabaseAdmin = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
      {
        auth: {
          autoRefreshToken: false,
          persistSession: false
        }
      }
    );

    // Create client for user authentication
    const supabaseClient = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_ANON_KEY") ?? ""
    );

    const authHeader = req.headers.get("Authorization");
    if (!authHeader) throw new Error("No authorization header provided");

    const token = authHeader.replace("Bearer ", "");
    const { data: userData, error: userError } = await supabaseClient.auth.getUser(token);
    if (userError) throw new Error(`Authentication error: ${userError.message}`);
    
    const user = userData.user;
    if (!user?.id) throw new Error("User not authenticated");
    logStep("User authenticated", { userId: user.id });

    const { action, amount, reason, documentId } = await req.json();
    
    if (!action || !['spend', 'earn', 'grant'].includes(action)) {
      throw new Error("Invalid action. Must be 'spend', 'earn', or 'grant'");
    }

    if (!amount || amount <= 0) {
      throw new Error("Amount must be a positive number");
    }

    logStep("Processing credit transaction", { action, amount, reason, documentId });

    // Map action to database type
    const typeMapping = {
      'spend': 'spent',
      'earn': 'earned', 
      'grant': 'granted'
    };

    // Use the database function to update credits
    const { data, error } = await supabaseAdmin.rpc('update_user_credits', {
      p_user_id: user.id,
      p_amount: action === 'spend' ? amount : amount,
      p_type: typeMapping[action as keyof typeof typeMapping],
      p_reason: reason || `Credit ${action}`,
      p_document_id: documentId || null
    });

    if (error) {
      logStep("Error updating credits", { error: error.message });
      throw new Error(`Failed to update credits: ${error.message}`);
    }

    if (data === false) {
      throw new Error("Insufficient credits for this operation");
    }

    // Get updated user profile
    const { data: profile, error: profileError } = await supabaseAdmin
      .from('profiles')
      .select('credits, credits_used, credits_earned')
      .eq('id', user.id)
      .single();

    if (profileError) {
      logStep("Error fetching updated profile", { error: profileError.message });
      throw new Error("Failed to fetch updated profile");
    }

    logStep("Credits updated successfully", { 
      newBalance: profile.credits,
      totalUsed: profile.credits_used,
      totalEarned: profile.credits_earned
    });

    return new Response(JSON.stringify({
      success: true,
      credits: profile.credits,
      credits_used: profile.credits_used,
      credits_earned: profile.credits_earned,
      message: `Successfully ${action === 'spend' ? 'spent' : action === 'earn' ? 'earned' : 'granted'} ${amount} credits`
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 200,
    });

  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logStep("ERROR in manage-credits", { message: errorMessage });
    
    return new Response(JSON.stringify({ 
      success: false,
      error: errorMessage 
    }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
      status: 400,
    });
  }
});
