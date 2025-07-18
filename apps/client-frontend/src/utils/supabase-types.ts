
export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[];

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          email: string;
          name: string | null;
          plan: 'free' | 'pro' | 'premium';
          credits: number;
          created_at: string;
        };
        Insert: {
          id: string;
          email: string;
          name?: string | null;
          plan?: 'free' | 'pro' | 'premium';
          credits?: number;
          created_at?: string;
        };
        Update: {
          id?: string;
          email?: string;
          name?: string | null;
          plan?: 'free' | 'pro' | 'premium';
          credits?: number;
          created_at?: string;
        };
      };
      // Add other table definitions as needed
    };
  };
}
