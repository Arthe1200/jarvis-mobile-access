# JARVIS Mobile Access

Page d'accueil statique pour ouvrir l'interface mobile de JARVIS depuis un iPhone.

## Publication avec GitHub Pages

1. Ouvre **Settings** dans ce dépôt.
2. Dans le menu **Pages**, sous **Build and deployment**, choisis **Deploy from a branch**.
3. Sélectionne la branche `main` et le dossier `/(root)`, puis clique sur **Save**.
4. Attends la fin du déploiement. L'adresse attendue sera :
   https://arthe1200.github.io/jarvis-mobile-access/

## Utilisation

La page demande l'adresse HTTPS actuelle du Cloudflare Quick Tunnel et ouvre ensuite `/mobile` sur ce tunnel. Elle peut mémoriser cette adresse uniquement dans le stockage local du navigateur sur cet appareil.

Le Quick Tunnel change généralement à chaque redémarrage : il faut donc saisir la nouvelle adresse quand cela arrive.

## Sécurité

- Ne committe jamais une adresse active de tunnel, un jeton DuckDNS, un mot de passe, une clé VAPID privée ou toute autre donnée secrète.
- Ne considère pas une adresse de tunnel comme une authentification. Toute personne qui obtient l'adresse peut essayer d'accéder à l'interface exposée.
- Pour une utilisation durable, protège l'accès à JARVIS avec une authentification solide ou une couche d'accès privée avant d'y connecter des fonctions sensibles.
