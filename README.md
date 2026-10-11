# JARVIS Mobile Access

Ce dépôt contient deux éléments :
- une page d'accès statique publiée avec GitHub Pages ;
- un premier prototype d'application iOS Capacitor, compilé sur un runner macOS de GitHub Actions.

## Page d'accès web

Adresse : https://arthe1200.github.io/jarvis-mobile-access/

La page demande l'adresse HTTPS actuelle du Cloudflare Quick Tunnel et ouvre ensuite `/mobile` sur ce tunnel. Le Quick Tunnel change généralement à chaque redémarrage, donc cette page ne peut pas découvrir automatiquement la nouvelle adresse.

## Construire le prototype iOS

1. Ouvre l'onglet **Actions** du dépôt : https://github.com/Arthe1200/jarvis-mobile-access/actions
2. Sélectionne **Build JARVIS iOS app**.
3. Clique sur **Run workflow**, puis confirme sur la branche `main`.
4. Attends que le workflow soit terminé avec le statut vert.
5. Ouvre l'exécution et télécharge l'artifact **JARVIS-unsigned-IPA**.

Le fichier produit est un IPA **non signé**. Il doit être signé avec ton identifiant Apple avant l'installation, par exemple via un outil de sideloading tel que Sideloadly. Avec un compte Apple gratuit, la signature personnelle est temporaire et doit généralement être renouvelée tous les 7 jours.

## État du prototype

L'écran iOS actuel est une coque de connexion : il mémorise localement une adresse HTTPS puis ouvre son chemin `/mobile`. Il ne contient pas encore l'interface complète issue de ton fichier local `mobile.html`, et ne découvre pas encore automatiquement ton PC. Pour intégrer toutes les fonctions JARVIS, il faudra importer une copie nettoyée de cette interface dans `native-app/www/` et concevoir une connexion stable et protégée.

## Sécurité

- Ne committe jamais une adresse active de tunnel, un jeton DuckDNS, un mot de passe, une clé VAPID privée ou toute autre donnée secrète.
- Ne considère pas une adresse de tunnel comme une authentification. Toute personne qui obtient l'adresse peut essayer d'accéder à l'interface exposée.
- Pour une utilisation durable, protège l'accès à JARVIS avec une authentification solide ou une couche d'accès privée avant d'y connecter des fonctions sensibles.
