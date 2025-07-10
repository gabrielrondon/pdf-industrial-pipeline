import { serve } from "https://deno.land/std@0.190.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2.45.0";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

const SHARE_CREDIT_REWARD = 5;

const logStep = (step: string, details?: any) => {
  const detailsStr = details ? ` - ${JSON.stringify(details)}` : '';
  console.log(`[TOGGLE-DOCUMENT-PRIVACY] ${step}${detailsStr}`);
};

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    logStep("Function started");

    const supabaseAdmin = createClient(
      Deno.env.get("SUPABASE_URL") ?? "",
      Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
      { auth: { persistSession: false } }
    );

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
    if (!user?.id) throw new Error("User not authenticated");
    logStep("User authenticated", { userId: user.id });

    const { documentId } = await req.json();
    if (!documentId) throw new Error("No documentId provided");

    const { data: doc, error: docError } = await supabaseAdmin
      .from('documents')
      .select('is_private, user_id')
      .eq('id', documentId)
      .single();
    if (docError || !doc) throw new Error("Documento não encontrado");
    if (doc.user_id !== user.id) throw new Error("Unauthorized");

    const { data: profile, error: profileError } = await supabaseAdmin
      .from('profiles')
      .select('plan')
      .eq('id', user.id)
      .single();
    if (profileError || !profile) throw new Error("Perfil não encontrado");

    const newPrivacyState = !doc.is_private;
    if (newPrivacyState && profile.plan === 'free') {
      logStep("Free user attempted private doc", { userId: user.id });
      return new Response(
        JSON.stringify({ success: false, error: 'Usuários do plano gratuito não podem manter documentos privados' }),
        { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 403 }
      );
    }

    const { error: updateError } = await supabaseAdmin
      .from('documents')
      .update({ is_private: newPrivacyState })
      .eq('id', documentId);
    if (updateError) throw new Error(`Erro ao alterar privacidade: ${updateError.message}`);

    if (!newPrivacyState && doc.is_private) {
      const { error: creditError } = await supabaseAdmin.rpc('update_user_credits', {
        p_user_id: user.id,
        p_amount: SHARE_CREDIT_REWARD,
        p_type: 'earned',
        p_reason: 'Compartilhamento de lead público',
        p_document_id: documentId
      });
      if (creditError) {
        logStep('Error awarding credits', { message: creditError.message });
      }
    }

    return new Response(
      JSON.stringify({ success: true, is_private: newPrivacyState }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 200 }
    );
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : String(error);
    logStep("ERROR in toggle-document-privacy", { message: errorMessage });
    return new Response(
      JSON.stringify({ success: false, error: errorMessage }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" }, status: 400 }
    );
  }
});
