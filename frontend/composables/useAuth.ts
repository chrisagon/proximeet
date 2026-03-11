import { PublicClientApplication, type AuthenticationResult } from "@azure/msal-browser";

const tokenKey = "proximeet_token";

// Instance MSAL globale partagée
let msalInstance: PublicClientApplication | null = null;
let msalInitPromise: Promise<PublicClientApplication> | null = null;

async function getMsalInstance(config: any): Promise<PublicClientApplication> {
  if (msalInstance) return msalInstance;
  
  if (msalInitPromise) return msalInitPromise;
  
  msalInitPromise = (async () => {
    const instance = new PublicClientApplication({
      auth: {
        clientId: config.public.msalClientId,
        authority: `https://login.microsoftonline.com/${config.public.msalTenantId}`,
        redirectUri: config.public.msalRedirectUri
      },
      cache: {
        cacheLocation: "localStorage"
      }
    });
    
    // CRITIQUE : Initialiser MSAL avant toute utilisation
    await instance.initialize();
    msalInstance = instance;
    return instance;
  })();
  
  return msalInitPromise;
}

export const useAuth = () => {
  const config = useRuntimeConfig();
  const account = ref<string | null>(null);
  const token = ref<string | null>(process.client ? localStorage.getItem(tokenKey) : null);

  const setToken = (accessToken: string | null) => {
    token.value = accessToken;
    if (process.client) {
      if (accessToken) {
        localStorage.setItem(tokenKey, accessToken);
      } else {
        localStorage.removeItem(tokenKey);
      }
    }
  };

  const handleRedirect = async () => {
    if (!process.client) return;
    const msal = await getMsalInstance(config);
    const result = await msal.handleRedirectPromise();
    if (result?.accessToken) {
      setToken(result.accessToken);
      account.value = result.account?.username || null;
    } else {
      const current = msal.getAllAccounts()[0];
      if (current) {
        account.value = current.username;
      }
    }
  };

  const login = async () => {
    if (!config.public.msalClientId || config.public.msalClientId === 'dummy') {
      alert("MSAL client id missing. Configure NUXT_PUBLIC_MSAL_CLIENT_ID.");
      return;
    }
    const msal = await getMsalInstance(config);
    await msal.loginRedirect({ scopes: config.public.msalScopes });
  };

  const logout = async () => {
    setToken(null);
    const msal = await getMsalInstance(config);
    await msal.logoutRedirect();
  };

  const acquireToken = async () => {
    const msal = await getMsalInstance(config);
    const current = msal.getAllAccounts()[0];
    if (!current) return null;
    const result: AuthenticationResult = await msal.acquireTokenSilent({
      account: current,
      scopes: config.public.msalScopes
    });
    if (result?.accessToken) {
      setToken(result.accessToken);
      return result.accessToken;
    }
    return null;
  };

  return { account, token, login, logout, acquireToken, handleRedirect, setToken };
};
