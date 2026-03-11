// Composable pour vérifier si l'utilisateur a complété l'onboarding
export const useOnboardingCheck = () => {
  const hasCompletedOnboarding = (): boolean => {
    if (!process.client) return false;
    
    // Vérifier si l'utilisateur a des coordonnées dans son profil
    const profileStr = localStorage.getItem("user_profile");
    if (!profileStr) return false;
    
    try {
      const profile = JSON.parse(profileStr);
      // L'utilisateur a complété l'onboarding s'il a des coordonnées (latitude ET longitude)
      return profile && 
             typeof profile.latitude === "number" && 
             typeof profile.longitude === "number";
    } catch {
      return false;
    }
  };

  const getRedirectPath = (): string => {
    return hasCompletedOnboarding() ? "/dashboard" : "/onboarding";
  };

  return { hasCompletedOnboarding, getRedirectPath };
};