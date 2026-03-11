import { test, expect } from '@playwright/test';

const helpCopy =
  'Voici comment utiliser Proximeet. 1. Choisissez d\\'abord un ou plusieurs restaurants favoris à proximité en cliquant sur "Restaurant". 2. Aller dans Tableau de bord : définissez votre position et cliquez sur Recherche de proximité. 3. Choisissez un des collègues à proximité 4. Définissez le jour et l\\'heure dans un de vos restaurants favoris. 5. Votre collègue accepte le rendez-vous. 6. Le rendez-vous apparait dans votre agenda.';

test('help modal is accessible from the navbar for all roles', async ({ page }) => {
  await page.goto('/');

  const helpButton = page.getByTestId('help-button');
  await expect(helpButton).toBeVisible();

  await helpButton.click();

  const modal = page.getByTestId('help-modal');
  await expect(modal).toBeVisible();
  await expect(modal).toHaveAttribute('role', 'dialog');
  await expect(modal.locator('.help-modal__text')).toHaveText(helpCopy);

  const closeButton = modal.locator('.help-modal__close');
  await expect(closeButton).toBeVisible();
  await closeButton.click();
  await expect(modal).toBeHidden();
});
