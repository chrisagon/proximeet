import type { FetchOptions } from 'ofetch';

export const useApi = () => {
  const config = useRuntimeConfig();
  const { token, acquireToken, handleRedirect } = useAuth();
  
  const api = async <T = any>(
    path: string, 
    options: FetchOptions = {}
  ): Promise<T> => {
    await handleRedirect();
    const accessToken = token.value || (await acquireToken());
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {})
    };
    
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
    }
    
    try {
      return await $fetch<T>(`${config.public.apiBase}${path}`, {
        ...options,
        headers
      });
    } catch (error: any) {
      if (error?.data?.detail) {
        throw new Error(error.data.detail);
      }
      throw error;
    }
  };
  
  return {
    get: <T = any>(path: string, options?: FetchOptions) => 
      api<T>(path, { ...options, method: 'GET' }),
    
    post: <T = any>(path: string, body?: any, options?: FetchOptions) => 
      api<T>(path, { ...options, method: 'POST', body }),
    
    patch: <T = any>(path: string, body?: any, options?: FetchOptions) => 
      api<T>(path, { ...options, method: 'PATCH', body }),
    
    delete: <T = any>(path: string, options?: FetchOptions) => 
      api<T>(path, { ...options, method: 'DELETE' })
  };
};